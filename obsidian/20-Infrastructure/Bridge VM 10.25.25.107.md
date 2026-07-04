# Bridge VM 10.25.25.107

## Identity

Role:
- Bridge VM.

Proxmox:
- Node/server: `aipve`
- VM ID: `12800`
- VM name: `u20-ROS1ROS2-bridge`

Observed hostname:
- `ros1ros2bridge`

Observed IPs:
- LAN: `10.25.25.107`
- Tailscale: `100.102.124.43`

Primary user:
- `swu`

Root/sudo:
- Required for systemd unit edits, service management, `/usr/local/bin`, and package installs.

## Responsibilities

Runs:
- ROS 1 Noetic environment.
- ROS 2 Foxy environment.
- ROS 1 -> ROS 2 dynamic bridge.
- ROS 2 rosbridge websocket.
- Topic advertiser helper.
- HTTP static map exporter.
- Bridge VM super repo and documentation.

## Important Services

- [[30-Services/ros-map-export.service]]
- [[30-Services/ros1-dynamic-bridge.service]]
- [[30-Services/rosbridge-websocket.service]]
- [[30-Services/rosbridge-topic-advertiser.service]]
- [[30-Services/ros-bridge.service Legacy]]

## Important Paths

- `/home/swu/map_exporter`
- `/home/swu/bridge_support`
- `/home/swu/bridge-vm-config-repo`
- `/home/swu/bridge-docs`
- `/home/swu/obsidian`
- `/usr/local/bin`
- `/etc/systemd/system`

## Current Known State

As of `2026-07-04`:
- HTTP map exporter active.
- Dynamic bridge active but upstream ROS 1 master is refusing/unavailable.
- Rosbridge websocket active on `9090`.
- Topic advertiser active.
- Legacy combined bridge masked.

## Related Notes

- [[20-Infrastructure/Machines and Access]]
- [[20-Infrastructure/Software Inventory]]
