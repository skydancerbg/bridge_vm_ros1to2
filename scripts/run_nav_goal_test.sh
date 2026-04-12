#!/usr/bin/env bash
set -euo pipefail

export ROS_MASTER_URI="${ROS_MASTER_URI:-http://10.25.25.115:11311}"
export ROS_IP="${ROS_IP:-10.25.25.107}"
export ROS_DISTRO="${ROS_DISTRO:-noetic}"
unset ROS_HOSTNAME ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION
set +u
source /opt/ros/noetic/setup.bash
set -u

exec python3 /home/swu/bridge-vm-config-repo/scripts/run_nav_goal_test_ros1.py "$@"
