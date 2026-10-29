#!/usr/bin/env python3
import hashlib
import json
import os
import threading
from array import array
from datetime import datetime, timezone

from flask import Flask, jsonify, send_from_directory
from PIL import Image
import rospy
from nav_msgs.srv import GetMap


HOST = "0.0.0.0"
PORT = 8081
OUTPUT_DIR = "/home/swu/map_exporter/output"
PNG_PATH = os.path.join(OUTPUT_DIR, "map.png")
META_PATH = os.path.join(OUTPUT_DIR, "map_meta.json")
# Both are nav_msgs/GetMap. `dynamic_map` comes first because it only exists while gmapping is
# running (P2.5's mapping session), and during a session it is the map that is actually growing;
# `static_map` is the map server's, which is what exists the rest of the time.
MAP_SERVICES = ("/robot/dynamic_map", "/robot/static_map")

app = Flask(__name__)
export_lock = threading.Lock()
map_service_proxy = None


def occupancy_to_grayscale(value):
    if value == -1:
        return 205
    if value >= 100:
        return 0
    if value <= 0:
        return 255
    return int(round(255 - (value * 255.0 / 100.0)))


def ensure_ros():
    """Connect to whichever map service is currently offered.

    Resolved on every export, not cached: which of the two exists is precisely what changes when
    a mapping session starts or stops, and a proxy held from before a session would keep calling
    a service that is no longer there.
    """
    global map_service_proxy
    if not rospy.core.is_initialized():
        rospy.init_node("ros_map_exporter", anonymous=False, disable_signals=True)

    for name in MAP_SERVICES:
        try:
            rospy.wait_for_service(name, timeout=3.0)
        except rospy.ROSException:
            continue
        map_service_proxy = rospy.ServiceProxy(name, GetMap)
        return name

    map_service_proxy = None
    raise RuntimeError(
        "no map service is available: tried %s. During a mapping session gmapping offers "
        "dynamic_map; otherwise the map server offers static_map. If neither is there, the "
        "simulation's navigation stack is down." % ", ".join(MAP_SERVICES)
    )


def export_map():
    source = ensure_ros()
    response = map_service_proxy()
    info = response.map.info

    pixels = [occupancy_to_grayscale(value) for value in response.map.data]
    image = Image.new("L", (info.width, info.height))
    image.putdata(pixels)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    # Write to a temporary file and rename it over the published one. os.replace is atomic on one
    # filesystem, so a reader fetching /map.png or /map_meta.json while a refresh runs sees the
    # old file or the new one, never half of either (F-012). The PNG goes first and the metadata
    # second: metadata that names a generation is only ever published after its image is in place.
    tmp_png = PNG_PATH + ".tmp"
    image.save(tmp_png, format="PNG")
    os.replace(tmp_png, PNG_PATH)

    # Identifies this map's content, not the moment it was exported: the same saved map gives the
    # same value on every refresh; a mapping session that saves a new map, or gmapping while it
    # builds one, gives a different one. Consumers compare it instead of timestamps.
    generation = hashlib.sha256(
        array("b", response.map.data).tobytes()
        + f"{info.width}x{info.height}@{info.resolution}".encode()
    ).hexdigest()[:16]

    meta = {
        "resolution": info.resolution,
        "width": info.width,
        "height": info.height,
        "origin": {
            "position": {
                "x": info.origin.position.x,
                "y": info.origin.position.y,
                "z": info.origin.position.z,
            },
            "orientation": {
                "qx": info.origin.orientation.x,
                "qy": info.origin.orientation.y,
                "qz": info.origin.orientation.z,
                "qw": info.origin.orientation.w,
            },
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image": "/map.png",
        # Which service this came from: dynamic_map means a mapping session was running and this
        # is a map still being built, static_map means it is the saved one being served.
        "source": source,
        "generation": generation,
    }

    tmp_meta = META_PATH + ".tmp"
    with open(tmp_meta, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2)
    os.replace(tmp_meta, META_PATH)

    return meta


def refresh_map(blocking=True):
    acquired = export_lock.acquire(blocking=blocking)
    if not acquired:
        raise RuntimeError("map refresh already in progress")
    try:
        return export_map()
    finally:
        export_lock.release()


@app.route("/")
def index():
    return jsonify(
        {
            "service": "ros-map-export",
            "endpoints": ["/", "/refresh", "/map.png", "/map_meta.json"],
            # Both, in the order they are tried: dynamic_map exists only while a mapping
            # session is running, static_map the rest of the time (P2.5).
            "map_services": list(MAP_SERVICES),
        }
    )


@app.route("/refresh")
def refresh():
    try:
        meta = refresh_map(blocking=False)
        return jsonify({"status": "ok", "meta": meta})
    except RuntimeError as exc:
        return jsonify({"status": "busy", "error": str(exc)}), 202
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


@app.route("/map.png")
def map_png():
    if not os.path.exists(PNG_PATH):
        try:
            refresh_map()
        except Exception as exc:
            return jsonify({"status": "error", "error": str(exc)}), 500
    return send_from_directory(OUTPUT_DIR, "map.png", mimetype="image/png")


@app.route("/map_meta.json")
def map_meta():
    if not os.path.exists(META_PATH):
        try:
            refresh_map()
        except Exception as exc:
            return jsonify({"status": "error", "error": str(exc)}), 500
    return send_from_directory(OUTPUT_DIR, "map_meta.json", mimetype="application/json")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    threading.Thread(target=refresh_map, daemon=True).start()
    app.run(host=HOST, port=PORT)
