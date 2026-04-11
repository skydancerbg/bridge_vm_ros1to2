#!/bin/bash

set -eo pipefail

unset ROS_HOSTNAME
export ROS_MASTER_URI=http://10.25.25.115:11311
export ROS_IP=$(hostname -I | awk '{print $1}')
export ROS_LOCALHOST_ONLY=0

start_dynamic_bridge() {
  set +u
  source /opt/ros/noetic/setup.bash
  source /opt/ros/foxy/setup.bash
  set -u

  exec ros2 run ros1_bridge dynamic_bridge --bridge-all-topics
}

start_rosbridge() {
  unset ROS_MASTER_URI
  unset ROS_ETC_DIR
  unset ROS_PACKAGE_PATH
  unset ROS_ROOT
  unset ROSLISP_PACKAGE_DIRECTORIES
  unset ROS_VERSION
  unset ROS_DISTRO

  set +u
  source /opt/ros/foxy/setup.bash
  set -u

  exec ros2 launch rosbridge_server rosbridge_websocket_launch.xml \
    max_message_size:=100000000 \
    address:=0.0.0.0
}

start_dynamic_bridge &
start_rosbridge &
wait
