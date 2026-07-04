# CURRENT STAGE

The current stage is stabilization and handoff for the split ROS 1 -> ROS 2 -> websocket bridge plus HTTP static map export.

Live architecture:
- `ros1-dynamic-bridge.service` runs the ROS 1 -> ROS 2 dynamic bridge through `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`.
- `rosbridge-websocket.service` runs rosbridge in a ROS 2-only environment on `0.0.0.0:9090`.
- `rosbridge-topic-advertiser.service` advertises `/robot/amcl_pose` and `/robot/robotnik_base_control/odom` types into ROS 2.
- `ros-map-export.service` serves `/map.png` and `/map_meta.json` on `0.0.0.0:8081`.
- Legacy combined `ros-bridge.service` is masked/retired and is not the current runtime path.

Current endpoints:
- `ws://10.25.25.107:9090`
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`
- Upstream ROS 1 master: `http://10.25.25.115:11311`

Current known issue / latest update:
- On `2026-07-03`, the bridge VM could not communicate with upstream ROS 1 master `10.25.25.115:11311`.
- On `2026-07-04`, the user started the simulation/ROS master on the sim VM and `/robot/static_map` became reachable again.
- `curl http://127.0.0.1:8081/refresh` succeeded on `2026-07-04`.
- Sim start command: `cd ~/catkin_ws && source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rb1_base_gazebo rb1_neo_workshop_navigation.launch`

Primary handoff:
- `/home/swu/bridge-docs/Handoff_03-06-26_v1.md` once installed with root permissions.
- Staged writable copy: `/home/swu/bridge-vm-config-repo/docs/Handoff_03-06-26_v1.md`.

Proxmox inventory:
- Node/server: `aipve`
- Bridge VM: ID `12800`, `u20-ROS1ROS2-bridge`, LAN `10.25.25.107`, Tailscale `100.102.124.43`
- Sim/ROS 1 VM: ID `12851`, `u20-RB1sim-ros1and2-bridge-geminicli`, LAN `10.25.25.115`, Tailscale `100.79.246.33`
- Future web app VM: ID `12850`, `u24ai-RobcoGADGET-web`, LAN `10.10.25.113`, Tailscale `100.121.18.83`
