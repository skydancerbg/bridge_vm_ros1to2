# Bridge Fresh-Chat Handoff

## Start Here
- This VM is the bridge and browser-facing robotics integration point.
- Authoritative bridge architecture is split-service:
  - `ros1-dynamic-bridge.service`
  - `rosbridge-websocket.service`
  - `ros-map-export.service`
- `ros-bridge.service` is retired and masked.

## Current State
- Major watchdog-driven restart collapse is fixed.
- Final watchdog rule:
  - restart only if ROS 1 odom publisher visibility is missing and bridged ROS 2 odom is also unhealthy for 3 consecutive checks
- Validated continuity in the fixed run:
  - ROS 2 odom max gap about `0.305 s`
  - websocket odom max gap about `0.302 s`
  - zero gaps over `0.5 s`
  - no watchdog-triggered restarts in that run
- Stale rosbridge after sim restart was separately handled by restarting `rosbridge-websocket.service` when needed.

## What Exists For Testing
- remote sim restart/status helpers
- RViz nav-goal capture helper
- repeatable 4-goal status-driven runner
- cancel helper
- nav-goal runner status helper

## Current Main Open Issue
- Main remaining issue is mostly UI-side marker smoothness/jumpiness.
- Do not represent waypoint saving as solved.

## Fast Checks
- `ps -ef | grep dynamic_bridge`
- `sudo ss -ltnp | grep 9090`
- `systemctl status ros1-dynamic-bridge.service --no-pager -l`
- `systemctl status rosbridge-websocket.service --no-pager -l`
- `curl http://127.0.0.1:8081/map_meta.json`
