# What Was Developed

## HTTP Map Exporter

Path:
- `/home/swu/map_exporter`

Files:
- `app.py`
- `run.sh`
- `output/map.png`
- `output/map_meta.json`

Developed behavior:
- Uses ROS 1 Noetic.
- Calls `/robot/static_map` via `nav_msgs/GetMap`.
- Converts OccupancyGrid into grayscale PNG.
- Vertically flips PNG for browser display.
- Writes metadata JSON with resolution, dimensions, origin, timestamp, and image path.
- Serves Flask endpoints on `0.0.0.0:8081`.
- Serves cached files even when upstream ROS 1 is unavailable.

## Split Bridge Services

Developed/installed service split:
- `ros1-dynamic-bridge.service`
- `rosbridge-websocket.service`
- `rosbridge-topic-advertiser.service`
- `ros-map-export.service`

Retired:
- `ros-bridge.service`

## Dynamic Bridge Watchdog

Path:
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`

Purpose:
- Launches `ros2 run ros1_bridge dynamic_bridge --bridge-all-topics`.
- Checks ROS 1 and ROS 2 odom paths.
- Avoids immediate restarts when upstream ROS 1 publishers are briefly absent.

## Topic Advertiser

Path:
- `/home/swu/bridge_support/ros2_topic_advertiser.py`

Purpose:
- Publishes topic type declarations into ROS 2 graph for rosbridge type inference.

Topics:
- `/robot/robotnik_base_control/odom`
- `/robot/amcl_pose`

## Super Repo

Path:
- `/home/swu/bridge-vm-config-repo`

Developed as:
- Git-ready mirror.
- Restore toolkit.
- Documentation store.
- Verification and remote operation script collection.

## Nav Goal Test Helpers

Path:
- `/home/swu/bridge-vm-config-repo/scripts`

Helpers:
- `capture_nav_goals_ros1.py`
- `run_nav_goal_test_ros1.py`
- `run_nav_goal_test.sh`
- `cancel_nav_goal_test.sh`
- `nav_goal_test_status.sh`

Purpose:
- Support repeatable bridge-side navigation goal testing.

## Remote Sim Helpers

Path:
- `/home/swu/bridge-vm-config-repo/scripts`

Helpers:
- `remote_sim_status.sh`
- `remote_sim_restart.sh`

Purpose:
- Check and restart the upstream sim/navigation stack on `10.25.25.115`.

