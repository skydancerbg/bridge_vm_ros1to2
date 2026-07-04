# rosbridge-websocket.service

## Purpose

Exposes ROS 2 topics to browser websocket clients on `ws://10.25.25.107:9090`.

## Live Unit

Path:
- `/etc/systemd/system/rosbridge-websocket.service`

Service properties:
- `User=swu`
- `WorkingDirectory=/home/swu`
- `Restart=always`
- Starts after and wants `ros1-dynamic-bridge.service`.

## Important Environment Behavior

The unit:
- Sets `ROS_IP=10.25.25.107`.
- Sets `ROS_LOCALHOST_ONLY=0`.
- Unsets ROS 1 variables including `ROS_MASTER_URI`, `ROS_PACKAGE_PATH`, `ROS_ROOT`, `ROS_VERSION`, `ROS_DISTRO`, and `ROS_HOSTNAME`.
- Sources `/opt/ros/foxy/setup.bash`.
- Runs `ros2 launch rosbridge_server rosbridge_websocket_launch.xml address:=0.0.0.0 max_message_size:=100000000`.

This ROS 2-only environment is intentional. Do not mix Noetic into this service.

## Current State

On `2026-07-04`, service was active and logs showed:

```text
Rosbridge WebSocket server started on port 9090
```

## Verify

```bash
systemctl status rosbridge-websocket.service --no-pager -l
ss -ltnp | grep 9090
ps -ef | grep rosbridge | grep -v grep
journalctl -u rosbridge-websocket.service --no-pager -l | tail -n 40
```

## Related Notes

- [[60-Decisions/ROS 2 Only Rosbridge Environment]]
- [[30-Services/rosbridge-topic-advertiser.service]]

