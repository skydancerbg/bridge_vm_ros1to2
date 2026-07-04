# Software Inventory

## Bridge VM Confirmed Packages

Confirmed on `10.25.25.107`:

| Package | Version |
| --- | --- |
| `ros-noetic-desktop-full` | `1.5.0-1focal.20250521.014741` |
| `ros-foxy-ros-base` | `0.9.2-1focal.20230606.035837` |
| `ros-foxy-ros1-bridge` | `0.9.7-1focal.20230527.055419` |
| `ros-foxy-rosbridge-server` | `1.3.1-1focal.20230527.054025` |
| `python3-flask` | `1.1.1-2ubuntu0.1` |
| `python3-pil` | `7.0.0-4ubuntu0.9` |
| `tailscale` | `1.98.4` |

## Important Runtime Tools

Used by the project:
- `systemd`
- `curl`
- `ss`
- `git`
- `rg`
- `python3`
- ROS 1 Noetic CLI tools
- ROS 2 Foxy CLI tools

## ROS Distributions

Installed and used:
- ROS 1 Noetic under `/opt/ros/noetic`
- ROS 2 Foxy under `/opt/ros/foxy`

Important environment rule:
- Source Noetic and Foxy together only where required by `ros1_bridge`.
- Keep rosbridge websocket and topic advertiser in ROS 2-only environment.

## Upstream Sim VM Software

The upstream sim VM at `10.25.25.115` was not directly inspected in the latest session because ROS master was unreachable.

Expected from existing scripts:
- ROS 1 simulation/navigation stack.
- `/home/swu/restart_neo_workshop_navigation.sh`.
- Catkin workspace at `~/catkin_ws`.
- Launch file package/path: `rb1_base_gazebo rb1_neo_workshop_navigation.launch`.
- Processes matching `rb1_neo_workshop_navigation`, `roslaunch`, `gazebo`, `gzserver`, or `gzclient` during active sim runs.
