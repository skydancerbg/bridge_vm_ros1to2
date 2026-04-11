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
CROP_MARGIN_PIXELS = 32

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


def compute_crop_bounds(data, width, height, margin):
    meaningful = [index for index, value in enumerate(data) if value != -1]
    if not meaningful:
        return 0, 0, width - 1, height - 1

    min_x = min(index % width for index in meaningful)
    max_x = max(index % width for index in meaningful)
    min_y = min(index // width for index in meaningful)
    max_y = max(index // width for index in meaningful)

    return (
        max(0, min_x - margin),
        max(0, min_y - margin),
        min(width - 1, max_x + margin),
        min(height - 1, max_y + margin),
    )


def export_map():
    ensure_ros()
    response = map_service_proxy()
    info = response.map.info
    data = list(response.map.data)

    min_x, min_y, max_x, max_y = compute_crop_bounds(
        data, info.width, info.height, CROP_MARGIN_PIXELS
    )
    cropped_width = max_x - min_x + 1
    cropped_height = max_y - min_y + 1

    cropped_data = []
    for row in range(min_y, max_y + 1):
        row_start = row * info.width + min_x
        row_end = row_start + cropped_width
        cropped_data.extend(data[row_start:row_end])

    pixels = [occupancy_to_grayscale(value) for value in cropped_data]
    image = Image.new("L", (cropped_width, cropped_height))
    image.putdata(pixels)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(PNG_PATH)

    meta = {
        "resolution": info.resolution,
        "width": cropped_width,
        "height": cropped_height,
        "origin": {
            "position": {
                "x": info.origin.position.x + (min_x * info.resolution),
                "y": info.origin.position.y + (min_y * info.resolution),
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
        "source_width": info.width,
        "source_height": info.height,
        "crop_margin_pixels": CROP_MARGIN_PIXELS,
    }

    with open(META_PATH, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2)

    return meta


def refresh_map():
    with export_lock:
        return export_map()


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
        meta = refresh_map()
        return jsonify({"status": "ok", "meta": meta})
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
    try:
        refresh_map()
    except Exception as exc:
        app.logger.warning("Initial map export failed: %s", exc)
    app.run(host=HOST, port=PORT)
