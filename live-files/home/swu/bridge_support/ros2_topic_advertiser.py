#!/usr/bin/env python3
"""ROS 2 type-inference helper for rosbridge.

rosbridge on the ROS 2 side needs a topic's type before it can subscribe. When a client sends the
type in its `subscribe` message it can do without help; when it does not, the topic has to exist
in the ROS 2 graph already. This node creates the publishers that put it there.

**Why /robot/amcl_pose is NOT advertised here (04.08.2026).**

A publisher created here is a *ROS 2* publisher. `dynamic_bridge` sees it, pairs it with any ROS 1
subscriber and builds a **2to1** bridge — at which point the bridge itself becomes a ROS 1
publisher of that topic, the **1to2** direction is dropped, and it is never re-created: the
bridge's own ROS 1 subscriber keeps justifying the reverse link. The topic then looks perfectly
healthy (`rostopic info` lists publishers and subscribers, both services are `active`) while no
message crosses from ROS 1 to ROS 2 at all.

That is exactly what happened to `/robot/amcl_pose`: AMCL published 59 poses during one rotation,
the browser received none, and the console sat on "awaiting localisation" for hours. Measured on
04.08.2026; stopping this publisher and restarting `ros1-dynamic-bridge` restored delivery
immediately — 82 pose frames in the next browser session.

Odometry is still advertised: it has not shown the same flip, and the gateway's Г6 live check
subscribes to it without a type. Anything that needs a topic which is not advertised here must
send its type in the subscribe — the operator console does, for every topic it reads.
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class TopicAdvertiser(Node):
    def __init__(self) -> None:
        super().__init__("rosbridge_topic_advertiser")
        self.odom_pub = self.create_publisher(
            Odometry, "/robot/robotnik_base_control/odom", 10
        )


def main() -> None:
    rclpy.init()
    node = TopicAdvertiser()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
