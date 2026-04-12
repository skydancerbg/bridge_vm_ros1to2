#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="${NAV_GOAL_TEST_RUNTIME_DIR:-/tmp/nav_goal_test}"
STOP_FILE="${RUNTIME_DIR}/stop.flag"

mkdir -p "${RUNTIME_DIR}"
: > "${STOP_FILE}"

export ROS_MASTER_URI="${ROS_MASTER_URI:-http://10.25.25.115:11311}"
export ROS_IP="${ROS_IP:-10.25.25.107}"
unset ROS_HOSTNAME ROS_DISTRO ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION
set +u
source /opt/ros/noetic/setup.bash
set -u

echo "cancelling active move_base goal"
exec rostopic pub -1 /robot/move_base/cancel actionlib_msgs/GoalID '{}'
