# PROJECT STATUS

## Current State
- `ros-map-export.service` is working and serving full-map static map artifacts.
- `ros1-dynamic-bridge.service` is running and forwarding ROS 1 topics into ROS 2.
- `rosbridge-websocket.service` is running separately in a ROS 2-only environment on port `9090`.
- `ros-bridge.service` is masked and must remain non-authoritative.
- Typed websocket delivery is confirmed for live `/robot/robotnik_base_control/odom`.
- The robot is visible and moving in the UI again after bridge-side runtime cleanup.
- `/robot/amcl_pose` is present, but it was not required for the successful fix.

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
- Frontend should consume exported map metadata dynamically and not assume old cropped dimensions or hard-coded map extents.
- First-response bridge troubleshooting should check `ps -ef | grep dynamic_bridge` and `sudo ss -ltnp | grep 9090` before any service-file edits.

## Last Verified
- Map export endpoints verified on `2026-04-11`, with full-map dimensions `4992 x 4992`.
- `9090` verified on `2026-04-11` as owned only by the intended managed rosbridge process.
- Live ROS 2 delivery confirmed for `/robot/robotnik_base_control/odom` on `2026-04-11`.
- Typed websocket subscribe confirmed publish delivery for `/robot/robotnik_base_control/odom` on `2026-04-11`.
- No rollback is needed for the current post-fix state.
