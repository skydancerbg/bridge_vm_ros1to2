# rosbridge-topic-advertiser.service

## Purpose

Advertises browser-consumed topic names and types into the ROS 2 graph so rosbridge can resolve subscriptions.

## Live Unit

Path:
- `/etc/systemd/system/rosbridge-topic-advertiser.service`

Script:
- `/home/swu/bridge_support/ros2_topic_advertiser.py`

## Advertised Topics

The helper creates ROS 2 publishers for:
- `/robot/robotnik_base_control/odom` as `nav_msgs/msg/Odometry`
- `/robot/amcl_pose` as `geometry_msgs/msg/PoseWithCovarianceStamped`

The helper spins without publishing actual data. Its role is type visibility.

## Environment

Like rosbridge websocket, this service runs in a ROS 2-only environment:
- `ROS_IP=10.25.25.107`
- `ROS_LOCALHOST_ONLY=0`
- ROS 1 variables unset
- `/opt/ros/foxy/setup.bash` sourced

## Verify

```bash
systemctl status rosbridge-topic-advertiser.service --no-pager -l
unset ROS_MASTER_URI ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION ROS_DISTRO ROS_HOSTNAME
export ROS_IP=10.25.25.107
export ROS_LOCALHOST_ONLY=0
source /opt/ros/foxy/setup.bash
ros2 topic list -t | egrep '/robot/amcl_pose|/robot/robotnik_base_control/odom'
```

## Related Notes

- [[60-Decisions/Topic Advertiser For Type Inference]]
- [[30-Services/rosbridge-websocket.service]]

