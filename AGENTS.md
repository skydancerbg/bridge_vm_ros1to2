# AGENTS

## Role
- This VM is the ROS integration point between the upstream ROS 1 system and browser-facing consumers.

## Scope
- Host the ROS 1 <-> ROS 2 bridge.
- Expose websocket access for frontend clients.
- Expose static map artifacts over HTTP.
- Preserve bridge startup conventions that keep ROS 2 discovery working.

## Owned Files And Services
- `/usr/local/bin/bridge_startup.sh`
- `/etc/systemd/system/ros-bridge.service`
- `/etc/systemd/system/ros1-dynamic-bridge.service`
- `/etc/systemd/system/rosbridge-websocket.service`
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`
- `/home/swu/map_exporter/ros-map-export.service`
- `/etc/systemd/system/ros-map-export.service`
- `ros1-dynamic-bridge.service`
- `rosbridge-websocket.service`
- `ros-map-export.service`

## Inputs
- Upstream ROS 1 master at `http://10.25.25.115:11311`
- ROS 1 topics and services from the upstream robot stack
- Static map service data from `/robot/static_map`

## Outputs
- Websocket endpoint: `ws://10.25.25.107:9090`
- Static map PNG: `http://10.25.25.107:8081/map.png`
- Static map metadata: `http://10.25.25.107:8081/map_meta.json`
- `ros-map-export.service` now crops the real ROS occupancy grid to the meaningful non-unknown area with a safety margin before publishing the PNG and metadata.
- Frontend-consumed topics currently include `/robot/amcl_pose` and `/robot/robotnik_base_control/odom`

## Must Not Break
- Do not casually redesign the bridge architecture.
- Do not move websocket off `9090`.
- Do not move map export off `8081`.
- `dynamic_bridge` must stay in its own service with the dual-source ROS 1 + ROS 2 environment.
- `rosbridge_websocket` must stay in its own service with a ROS 2-only environment.
- Do not modify map export service logic during bridge-only work unless map export is actually broken.

## Restart/Resume Notes
- Verify `ros1-dynamic-bridge.service` and `rosbridge-websocket.service` separately with `systemctl status`.
- Verify websocket binding with `ss -ltnp | grep 9090`.
- Verify `ros-map-export.service` with `systemctl status` and HTTP fetches on port `8081`.
- Frontend must consume current map metadata dynamically because exported map dimensions and origin now reflect cropped content.
- Treat the split bridge services as authoritative; `ros-bridge.service` is retired.
- If frontend pose delivery is questioned, compare `/robot/amcl_pose` with `/robot/robotnik_base_control/odom`.
