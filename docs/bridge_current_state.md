# Bridge Current State

## Summary
- Split-service bridge architecture remains authoritative:
  - `ros1-dynamic-bridge.service`
  - `rosbridge-websocket.service`
  - `ros-map-export.service`
- Legacy `ros-bridge.service` remains retired, masked, and non-authoritative.
- Major watchdog-driven bridge restart collapse is fixed.
- Remaining main project issue is mostly UI-side marker motion smoothness and residual visual jumpiness, not catastrophic bridge transport collapse.
- Waypoint saving is not claimed solved in this stage.

## Bridge Runtime State
- `ros1_dynamic_bridge_watchdog.sh` now restarts the bridge only if:
  - ROS 1 odom publisher visibility is missing
  - and bridged ROS 2 odom is also unhealthy
  - for 3 consecutive checks
- Stale rosbridge after simulation restart was separately identified earlier; restarting `rosbridge-websocket.service` fixed stale handshake-without-odom cases.
- `rosbridge-websocket.service` remained stable in the validated post-fix run.

## Measured Post-Fix Continuity
- `ROS2_MAX_GAP_SEC` about `0.305`
- `WS_MAX_GAP_SEC` about `0.302`
- no measured gaps over `0.5 s` in the validated post-fix run
- no watchdog-triggered restarts occurred in that validated post-fix run

## Current Browser-Facing Endpoints
- `ws://10.25.25.107:9090`
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`

## Current Topics
- Preferred pose topic remains `/robot/amcl_pose` when it is fresh
- Reliable fallback and main validated live pose feed is `/robot/robotnik_base_control/odom`
- Repeatable nav-goal input topic is `/robot/move_base_simple/goal`

## Bridge-Side Test Automation
- `scripts/remote_sim_restart.sh`
- `scripts/remote_sim_status.sh`
- `scripts/capture_nav_goals_ros1.py`
- `scripts/run_nav_goal_test_ros1.py`
- `scripts/run_nav_goal_test.sh`
- `scripts/cancel_nav_goal_test.sh`
- `scripts/nav_goal_test_status.sh`

## Captured Repeatable Nav Goals
- A 4-goal repeatable RViz 2D Nav Goal set exists on the bridge side and is used by the status-driven goal runner.

## Remote Sim-Control Workflow
- Passwordless SSH from bridge VM to sim VM is confirmed for:
  - `swu@10.25.25.115`
  - `root@10.25.25.115`
- Confirmed sim restart entrypoint on the sim VM:
  - `/home/swu/restart_neo_workshop_navigation.sh`
- Important caveat:
  - a prior simulation terminal may remain hung and may need `Ctrl-C` or terminal/window cleanup before a new launch behaves normally
