# Bridge Full Project Documentation

## System Role
- This VM is the ROS bridge and browser-facing integration point.
- Upstream ROS 1 master is `10.25.25.115:11311`.

## Authoritative Architecture
- `ros1-dynamic-bridge.service`
  - runs ROS 1 to ROS 2 topic bridging
  - uses `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`
- `rosbridge-websocket.service`
  - exposes ROS 2 topics to websocket clients on `9090`
  - must remain in a ROS 2-only environment
- `ros-map-export.service`
  - exposes the browser-facing static map on `8081`
- `ros-bridge.service`
  - legacy combined service
  - retired, masked, non-authoritative

## Important Runtime Files
- `/etc/systemd/system/ros1-dynamic-bridge.service`
- `/etc/systemd/system/rosbridge-websocket.service`
- `/etc/systemd/system/ros-map-export.service`
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`

## Verified Endpoints
- `ws://10.25.25.107:9090`
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`

## Bridge Recovery and Watchdog Policy
- Earlier project failures were caused by watchdog-driven bridge restarts and stale rosbridge cases after simulation restarts.
- Final watchdog policy in the current stage:
  - do not restart on ROS 1 publisher absence alone
  - restart only if ROS 1 odom publisher visibility is missing and bridged ROS 2 odom is also unhealthy for 3 consecutive checks
- This removed the repeated restart loop during repeatable navigation validation.

## Continuity Result At Current Stage
- Post-fix validated run:
  - `ROS2_MAX_GAP_SEC` about `0.305`
  - `WS_MAX_GAP_SEC` about `0.302`
  - zero measured gaps over `0.5 s`
  - no watchdog-triggered restarts during the validated post-fix run

## Sim Restart Notes
- Remote access from bridge VM to sim VM is confirmed with passwordless SSH.
- Standard sim restart entrypoint:
  - `/home/swu/restart_neo_workshop_navigation.sh`
- Remote helper scripts exist in this repo for status and restart.

## Repeatable Navigation Test Tooling
- Captured RViz 2D Nav Goals exist and are used as a repeatable test set.
- Status-driven runner waits for real navigation completion/failure rather than using blind sleeps.
- Active test can be cancelled from the bridge side.
- Current test helper set:
  - `scripts/capture_nav_goals_ros1.py`
  - `scripts/run_nav_goal_test_ros1.py`
  - `scripts/run_nav_goal_test.sh`
  - `scripts/cancel_nav_goal_test.sh`
  - `scripts/nav_goal_test_status.sh`

## Current Open Issue
- Main remaining project issue is mostly UI-side visible marker smoothness and jumpiness.
- Major bridge collapse and transport instability are no longer the primary issue in the current validated state.
- Waypoint saving should not be represented as solved in this stage.
