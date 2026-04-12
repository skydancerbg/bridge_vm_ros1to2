# PROJECT STATUS

## Current State
- `ros-map-export.service` is working and serving full-map static map artifacts.
- `ros1-dynamic-bridge.service` is running and forwarding ROS 1 topics into ROS 2.
- `ros1_dynamic_bridge_watchdog.sh` now requires both ROS 1 odom publisher absence and unhealthy ROS 2 bridged odom for 3 consecutive checks before it forces a bridge restart.
- `rosbridge-websocket.service` is running separately in a ROS 2-only environment on port `9090`.
- Websocket delivery is confirmed for live `/robot/robotnik_base_control/odom`.
- Repeatable bridge-side nav-goal capture and 4-goal test helpers are present in `scripts/`.
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
- `scripts/run_nav_goal_test.sh` and the remote sim helpers are intended to be callable from the normal bridge-side Codex `/root` session.
- `rosbridge_websocket` must stay in ROS 2-only subprocess context for DDS discovery behavior to remain correct.
- Frontend uses static map over HTTP and live pose over websocket.
- Frontend should consume exported map metadata dynamically and not assume old cropped dimensions or hard-coded map extents.
- Passwordless SSH from the bridge VM to the sim VM is confirmed for `swu@10.25.25.115` and `root@10.25.25.115`.
- The confirmed sim restart path on the sim VM is `/home/swu/restart_neo_workshop_navigation.sh`.
- The previous sim launcher terminal may remain hung after restart attempts and may need `Ctrl-C` or terminal/window cleanup before the new launch behaves normally.

## Last Verified
- Map export endpoints on `2026-04-11`, with full-map dimensions `4992 x 4992` restored and full-map origin active again.
- Split bridge services verified on `2026-04-12`.
- Websocket listener on `9090` on `2026-04-12`.
- Live ROS 2 and websocket delivery confirmed for `/robot/robotnik_base_control/odom` on `2026-04-12`.
- Major watchdog-driven bridge restart collapses were eliminated on `2026-04-12`; measured odom continuity dropped from multi-second outages to about `0.30 s` max gap with zero gaps over `0.5 s` in the validated run.
- Repeatable nav-goal capture and 4-goal status-driven runner helpers were validated on `2026-04-12`.
- `/robot/amcl_pose` type/path confirmed, but fresh live delivery not confirmed during the latest test window on `2026-04-10`.
- UI-side hide/reappear collapse is mostly resolved after the combined bridge and UI fixes; remaining issues are mostly visual smoothing and jumpiness rather than major transport collapse.
