# PROJECT STATUS

Last updated: `2026-07-04` on bridge VM `ros1ros2bridge`.

Current state:
- `ros-map-export.service` is active and serving full-map static artifacts on `8081`.
- `ros1-dynamic-bridge.service` is active and owns the ROS 1 -> ROS 2 dynamic bridge runtime.
- `rosbridge-websocket.service` is active and listening on `0.0.0.0:9090`.
- `rosbridge-topic-advertiser.service` is active and advertises browser-consumed topic types into ROS 2.
- Legacy `ros-bridge.service` is masked/retired and should remain non-authoritative.
- ROS 1 master at `http://10.25.25.115:11311` was reachable again on `2026-07-04`.
- `curl http://127.0.0.1:8081/refresh` succeeded on `2026-07-04`.
- GitHub deploy-key SSH auth works for `skydancerbg/bridge_vm_ros1to2`.
- Git remote `origin` uses `git@github.com:skydancerbg/bridge_vm_ros1to2.git`.

Working HTTP checks:
- `curl http://127.0.0.1:8081/` returns service metadata.
- `curl http://127.0.0.1:8081/map_meta.json` returns map metadata.
- `curl -I http://127.0.0.1:8081/map.png` returns `200 OK` and `Content-Type: image/png`.

Current map metadata:
- Resolution: `0.019999999552965164`
- Width: `4992`
- Height: `4992`
- Origin position: `x=-50.0`, `y=-50.0`, `z=0.0`
- Origin orientation: `qx=0.0`, `qy=0.0`, `qz=0.0`, `qw=1.0`
- Image path in metadata: `/map.png`

Network:
- Bridge VM LAN IP: `10.25.25.107`
- Bridge VM Tailscale IP: `100.102.124.43`
- Upstream ROS 1 master / sim VM: `10.25.25.115`
- Upstream ROS 1 master / sim VM Tailscale IP: `100.79.246.33`
- Future Robot Control Center web app VM LAN IP: `10.25.25.113`
- Future Robot Control Center web app VM Tailscale IP: `100.121.18.83`
- Default gateway: `10.25.25.1`

Proxmox inventory:
- Proxmox server/node: `aipve`
- Bridge VM: ID `12800`, name `u20-ROS1ROS2-bridge`
- Sim/ROS 1 VM: ID `12851`, name `u20-RB1sim-ros1and2-bridge-geminicli`
- Future web app VM: ID `12850`, name `u24ai-RobcoGADGET-web`

Frontend endpoints:
- `ws://10.25.25.107:9090`
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`

Passwordless access needed from a new development VM:
- `swu@10.25.25.107` for this bridge VM.
- A sudo-capable path on `10.25.25.107`, ideally passwordless sudo for service management.
- `swu@10.25.25.115` for the upstream sim/ROS 1 master VM.
- `root@10.25.25.115` if deeper sim-control access is needed.
- `user@10.25.25.113` for future Robot Control Center web app development.
- A sudo-capable path on `10.25.25.113` for web app runtime/deployment work.

Known constraint:
- On `2026-07-03`, `ROS_MASTER_URI=http://10.25.25.115:11311` was unreachable from this VM.
- On `2026-07-04`, the user started the simulation/ROS master on the sim VM and `/robot/static_map` was reachable again from the bridge VM.
- Confirmed sim start command on `10.25.25.115`: `cd ~/catkin_ws && source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rb1_base_gazebo rb1_neo_workshop_navigation.launch`

GitHub status:
- SSH auth test succeeds with `ssh -o BatchMode=yes -T git@github.com`.
- Push command is `cd /home/swu/bridge-vm-config-repo && git push origin main`.
