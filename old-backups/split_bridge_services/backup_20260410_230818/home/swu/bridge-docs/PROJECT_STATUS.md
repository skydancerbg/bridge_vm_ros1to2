# PROJECT STATUS

## Current State
- `ros-map-export.service` is working and serving cropped static map artifacts.
- `ros1-dynamic-bridge.service` is running and forwarding ROS 1 topics into ROS 2.
- `rosbridge-websocket.service` is running separately in a ROS 2-only environment on port `9090`.
- Websocket delivery is confirmed for live `/robot/robotnik_base_control/odom`.
- `/robot/amcl_pose` remains the preferred frontend pose topic, but recent bridge-side checks did not observe fresh live messages during the last verification window.

## Working Endpoints
- `ws://10.25.25.107:9090`
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`

## Active Topics
- `/robot/amcl_pose`
- `/robot/robotnik_base_control/odom`

## Known Constraints
- ROS 1 master is upstream at `10.25.25.115:11311`.
- This VM depends on upstream ROS 1 publishers and services.
- `dynamic_bridge` needs access to both ROS 1 and ROS 2 environments.
- `rosbridge_websocket` must stay in ROS 2-only subprocess context for DDS discovery behavior to remain correct.
- Frontend uses static map over HTTP and live pose over websocket.
- Frontend must honor exported map metadata dynamically because width, height, and origin now reflect cropped map extent.

## Last Verified
- Map export endpoints on `2026-04-10`, with source dimensions `4992 x 4992`, cropped export dimensions `644 x 775`, crop margin `32` pixels, and origin updated accordingly.
- Split bridge services verified on `2026-04-10`.
- Websocket listener on `9090` on `2026-04-10`.
- Live ROS 2 and websocket delivery confirmed for `/robot/robotnik_base_control/odom` on `2026-04-10`.
- `/robot/amcl_pose` type/path confirmed, but fresh live delivery not confirmed during the latest test window on `2026-04-10`.
