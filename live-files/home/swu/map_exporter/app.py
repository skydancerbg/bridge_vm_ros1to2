#!/usr/bin/env python3
import json
import os
import threading
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
MAP_SERVICE = "/robot/static_map"

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
    global map_service_proxy
    if not rospy.core.is_initialized():
        rospy.init_node("ros_map_exporter", anonymous=False, disable_signals=True)
    if map_service_proxy is None:
        rospy.wait_for_service(MAP_SERVICE, timeout=15.0)
        map_service_proxy = rospy.ServiceProxy(MAP_SERVICE, GetMap)


def export_map():
    ensure_ros()
    response = map_service_proxy()
    info = response.map.info

    pixels = [occupancy_to_grayscale(value) for value in response.map.data]
    image = Image.new("L", (info.width, info.height))
    image.putdata(pixels)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(PNG_PATH)

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
    }

    with open(META_PATH, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2)

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
            "map_service": MAP_SERVICE,
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
