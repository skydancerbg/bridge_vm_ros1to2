#!/usr/bin/env python3
import argparse
import json
import math
import signal
import sys
import time

import rospy
from geometry_msgs.msg import PoseStamped


def quat_to_yaw(x, y, z, w):
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def main():
    parser = argparse.ArgumentParser(description="Capture ROS 1 RViz 2D Nav Goals.")
    parser.add_argument("--topic", default="/robot/move_base_simple/goal")
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    args = parser.parse_args()

    state = {"count": 0, "timed_out": False}

    def handle_signal(signum, frame):
        raise KeyboardInterrupt

    def callback(msg):
        if state["count"] >= args.count:
            return
        state["count"] += 1
        yaw = quat_to_yaw(
            msg.pose.orientation.x,
            msg.pose.orientation.y,
            msg.pose.orientation.z,
            msg.pose.orientation.w,
        )
        payload = {
            "sequence_number": state["count"],
            "frame_id": msg.header.frame_id,
            "x": msg.pose.position.x,
            "y": msg.pose.position.y,
            "z": msg.pose.position.z,
            "qx": msg.pose.orientation.x,
            "qy": msg.pose.orientation.y,
            "qz": msg.pose.orientation.z,
            "qw": msg.pose.orientation.w,
            "yaw": yaw,
            "timestamp": {
                "secs": msg.header.stamp.secs,
                "nsecs": msg.header.stamp.nsecs,
            },
        }
        print(json.dumps(payload, sort_keys=True), flush=True)
        if state["count"] >= args.count:
            rospy.signal_shutdown("captured requested goal count")

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    rospy.init_node("capture_nav_goals_ros1", anonymous=True)
    rospy.Subscriber(args.topic, PoseStamped, callback, queue_size=10)
    deadline = time.monotonic() + args.timeout_seconds
    try:
        while not rospy.is_shutdown():
            if state["count"] >= args.count:
                break
            if time.monotonic() >= deadline:
                state["timed_out"] = True
                rospy.signal_shutdown("timeout reached")
                break
            rospy.sleep(0.1)
    except KeyboardInterrupt:
        pass
    summary = {
        "summary": {
            "requested_count": args.count,
            "captured_count": state["count"],
            "timed_out": state["timed_out"],
        }
    }
    print(json.dumps(summary, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
