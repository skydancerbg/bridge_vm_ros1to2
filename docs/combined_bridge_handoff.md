# Combined Bridge Handoff

## Current Operational Baseline
- Bridge VM uses split services only:
  - `ros1-dynamic-bridge.service`
  - `rosbridge-websocket.service`
  - `ros-map-export.service`
- Legacy `ros-bridge.service` stays masked and non-authoritative.

## What Was Fixed
- Major watchdog-driven dynamic bridge restart loop is fixed.
- Final rule:
  - restart only if ROS 1 odom publisher visibility is missing and bridged ROS 2 odom is also unhealthy for 3 consecutive checks
- Stale rosbridge after sim restart was also identified earlier; restarting `rosbridge-websocket.service` fixed stale handshake-without-odom cases.

## Current Measured Result
- `ROS2_MAX_GAP_SEC` about `0.305`
- `WS_MAX_GAP_SEC` about `0.302`
- zero measured gaps over `0.5 s` in the validated post-fix run
- no watchdog-triggered restarts in that validated post-fix run

## Testing Workflow Now Available
- remote sim restart/status helpers exist
- RViz goal capture helper exists
- repeatable status-driven 4-goal runner exists
- active-goal cancel helper exists
- nav-goal runner status helper exists

## Current Caveats
- `/robot/amcl_pose` still needs fresh/live validation when AMCL is actively updating
- `/robot/robotnik_base_control/odom` remains the reliable live fallback
- UI marker motion can still look jumpy because remaining issues are now mostly visual smoothing related
- waypoint saving is not claimed solved here

## Immediate Resume Guidance
- First check:
  - `ps -ef | grep dynamic_bridge`
  - `sudo ss -ltnp | grep 9090`
- Then verify:
  - `systemctl status ros1-dynamic-bridge.service --no-pager -l`
  - `systemctl status rosbridge-websocket.service --no-pager -l`
  - `systemctl status ros-map-export.service --no-pager -l`

## Remote Sim Control
- Confirmed SSH access from bridge VM to sim VM:
  - `ssh swu@10.25.25.115`
  - `ssh root@10.25.25.115`
- Standard sim restart command on sim VM:
  - `/home/swu/restart_neo_workshop_navigation.sh`
- Old sim launcher terminals may remain hung and may need manual cleanup.
