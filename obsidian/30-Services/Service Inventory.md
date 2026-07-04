# Service Inventory

## Current Active Services

| Service | Status | Purpose |
| --- | --- | --- |
| [[30-Services/ros-map-export.service]] | Active | Serves static map PNG and metadata over HTTP. |
| [[30-Services/ros1-dynamic-bridge.service]] | Active | Bridges ROS 1 topics into ROS 2. |
| [[30-Services/rosbridge-websocket.service]] | Active | Exposes ROS 2 topics to browser websocket clients. |
| [[30-Services/rosbridge-topic-advertiser.service]] | Active | Advertises important topic types for rosbridge. |

## Retired Service

| Service | Status | Purpose |
| --- | --- | --- |
| [[30-Services/ros-bridge.service Legacy]] | Masked | Old combined bridge runtime, retained only for reference. |

## Service Files

Live unit files:
- `/etc/systemd/system/ros-map-export.service`
- `/etc/systemd/system/ros1-dynamic-bridge.service`
- `/etc/systemd/system/rosbridge-websocket.service`
- `/etc/systemd/system/rosbridge-topic-advertiser.service`
- `/etc/systemd/system/ros-bridge.service`

Mirrored in super repo:
- `/home/swu/bridge-vm-config-repo/live-files/etc/systemd/system/`

## Related Notes

- [[40-Operations/Verification Commands]]
- [[40-Operations/Recovery Playbooks]]

