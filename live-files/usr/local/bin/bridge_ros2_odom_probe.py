#!/usr/bin/env python3
"""ROS 2 side health probe for the dynamic-bridge watchdog.

Lives in its own file, and is run by the watchdog through `env -i` with **only** the Foxy
environment, because that is the whole point of it. The watchdog script sources noetic and foxy
together; in that mixed environment rclpy sees an empty graph — measured: 0 messages and 0
publishers, against 1325 messages and 1 publisher for the identical probe run under Foxy alone.
So this check used to fail unconditionally, the watchdog restarted the bridge about once a
minute, and every restart destroyed the ROS 2 publishers that rosbridge had matched — which is
what left the browser read path silently dead.

Exit 0 if at least one Odometry message arrives inside the window, 1 otherwise.
"""

import time

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

TOPIC = "/robot/robotnik_base_control/odom"
# Generous relative to observed discovery (sub-second once the graph is healthy), so that a slow
# join is never mistaken for a dead bridge. The cost of waiting is nothing; the cost of a false
# negative is a restart that breaks every subscriber.
WINDOW_SECONDS = 30.0


def main() -> int:
    rclpy.init()
    node = Node("bridge_odom_watchdog")
    received = [0]
    node.create_subscription(
        Odometry, TOPIC, lambda _msg: received.__setitem__(0, received[0] + 1), 10
    )

    deadline = time.time() + WINDOW_SECONDS
    while time.time() < deadline and received[0] == 0:
        rclpy.spin_once(node, timeout_sec=0.5)

    node.destroy_node()
    rclpy.shutdown()
    return 0 if received[0] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
