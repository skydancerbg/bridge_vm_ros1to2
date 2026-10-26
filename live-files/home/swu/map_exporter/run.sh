#!/bin/bash

unset ROS_HOSTNAME
export ROS_MASTER_URI=http://10.25.25.123:11311
export ROS_IP=$(hostname -I | awk '{print $1}')
source /opt/ros/noetic/setup.bash
set -euo pipefail

exec python3 /home/swu/map_exporter/app.py
