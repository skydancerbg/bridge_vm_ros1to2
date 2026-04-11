#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped


class TopicAdvertiser(Node):
    def __init__(self) -> None:
        super().__init__("rosbridge_topic_advertiser")
        self.odom_pub = self.create_publisher(
            Odometry, "/robot/robotnik_base_control/odom", 10
        )
        self.amcl_pub = self.create_publisher(
            PoseWithCovarianceStamped, "/robot/amcl_pose", 10
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
