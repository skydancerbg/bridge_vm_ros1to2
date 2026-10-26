#!/bin/bash

set -eo pipefail
ROS_IP_VALUE=$(hostname -I | awk '{print $1}')

start_dynamic_bridge() {
  exec env -i \
    HOME=/home/swu \
    USER=swu \
    LOGNAME=swu \
    PATH=/usr/sbin:/usr/bin:/sbin:/bin \
    /bin/bash -lc '
      export ROS_MASTER_URI=http://10.25.25.123:11311
      export ROS_IP='"$ROS_IP_VALUE"'
      export ROS_LOCALHOST_ONLY=0
      unset ROS_HOSTNAME
      set +u
      source /opt/ros/noetic/setup.bash
      source /opt/ros/foxy/setup.bash
      set -u
      exec ros2 run ros1_bridge dynamic_bridge --bridge-all-topics
    '
}

start_rosbridge() {
  exec env -i \
    HOME=/home/swu \
    USER=swu \
    LOGNAME=swu \
    PATH=/usr/sbin:/usr/bin:/sbin:/bin \
    /bin/bash -lc '
      export ROS_IP='"$ROS_IP_VALUE"'
      export ROS_LOCALHOST_ONLY=0
      unset ROS_MASTER_URI ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION ROS_DISTRO ROS_HOSTNAME
      set +u
      source /opt/ros/foxy/setup.bash
      set -u
      exec ros2 launch rosbridge_server rosbridge_websocket_launch.xml \
        max_message_size:=100000000 \
        address:=0.0.0.0
    '
}

start_dynamic_bridge &
start_rosbridge &
wait
