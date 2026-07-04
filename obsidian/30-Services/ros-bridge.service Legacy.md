# ros-bridge.service Legacy

## Status

`ros-bridge.service` is masked and retired.

It is not the current bridge runtime and should not be restarted during normal development.

## Former Purpose

The old combined approach launched:
- ROS 1 -> ROS 2 dynamic bridge.
- rosbridge websocket.

This was replaced by split services:
- [[30-Services/ros1-dynamic-bridge.service]]
- [[30-Services/rosbridge-websocket.service]]
- [[30-Services/rosbridge-topic-advertiser.service]]
- [[30-Services/ros-map-export.service]]

## Related Files

- `/etc/systemd/system/ros-bridge.service`
- `/etc/systemd/system/ros-bridge.service.legacy-disabled`
- `/etc/systemd/system/ros-bridge.service.retired`
- `/usr/local/bin/bridge_startup.sh`

## Guardrail

Do not unmask or restart this service unless intentionally rolling back from the split architecture.

