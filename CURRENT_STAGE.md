# CURRENT STAGE

The current stage is stabilization and handoff for the split ROS 1 -> ROS 2 -> websocket bridge plus HTTP static map export.

Live architecture:
- `ros1-dynamic-bridge.service` runs the ROS 1 -> ROS 2 dynamic bridge through `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`.
- `rosbridge-websocket.service` runs rosbridge in a ROS 2-only environment on `0.0.0.0:9090`.
- `rosbridge-topic-advertiser.service` advertises `/robot/amcl_pose` and `/robot/robotnik_base_control/odom` types into ROS 2.
- `ros-map-export.service` serves `/map.png` and `/map_meta.json` on `0.0.0.0:8081`.
- Legacy combined `ros-bridge.service` is masked/retired and is not the current runtime path.

Current endpoints:
- `ws://10.25.25.108:9090`
- `http://10.25.25.108:8081/map.png`
- `http://10.25.25.108:8081/map_meta.json`
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
- Bridge VM: ID `12800`, `u20-ROS1ROS2-bridge`, LAN `10.25.25.108`, Tailscale `100.102.124.43`
- Sim/ROS 1 VM: ID `12851`, `u20-RB1sim-ros1and2-bridge-geminicli`, LAN `10.25.25.115`, Tailscale `100.79.246.33`
- Future web app VM: ID `12850`, `u24ai-RobcoGADGET-web`, LAN `10.10.25.113`, Tailscale `100.121.18.83`

## ⚠ DDS on this host: shared memory is broken — UDP only (04.08.2026)

FastDDS cannot initialise its shared-memory ports here:

```
[RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_portNNNN: open_and_lock_file failed
```

In Foxy that transport is builtin and carries same-host traffic, so **local ROS 2 communication
is intermittent without a workaround** — usually broken, occasionally fine. That intermittency
made it look like several unrelated faults over several days: rosbridge appearing not to join the
graph, probes that received hundreds of messages once and nothing the next time, discovery that
seemed merely slow, and the dynamic bridge restarting forever because its own health probe could
not see a publisher that was there.

**Every ROS 2 process on this VM must run with:**

```
FASTRTPS_DEFAULT_PROFILES_FILE=/etc/robco/fastdds_udp_only.xml
```

That profile declares a UDPv4 transport with `useBuiltinTransports=false`. It is already set in
`rosbridge-websocket.service`, `rosbridge-topic-advertiser.service` and in
`ros1_dynamic_bridge_watchdog.sh` (which covers the dynamic bridge, and passes the variable
explicitly into its ROS 2 probe because that runs under `env -i`). **Anything new added here
needs it too.**

The host also requires a multicast route for DDS discovery, persisted in the NetworkManager
profile:

```
224.0.0.0/4 dev enp6s18 scope link
```

Without it, two processes on this host cannot discover each other at all.

### The watchdog's health checks

`ros1_dynamic_bridge_watchdog.sh` sources noetic and foxy together, and **both** of its checks
were silently broken by that:

- `rostopic` fails on *import* with both distros on `PYTHONPATH`, so the ROS 1 check could never
  pass.
- `rclpy` sees an empty graph in the same environment — measured, 0 publishers against 1 under
  Foxy alone — so the ROS 2 check could never pass either.

Both now run in isolated environments; the ROS 2 probe lives in
`/usr/local/bin/bridge_ros2_odom_probe.py` so it can be read and run by hand. Before these fixes
the restart counter had reached **9 600+**; after them the bridge holds steady for hours.

### Diagnosing this class of fault

**Never use `ros2 topic list` / `info` / `echo` as evidence.** Foxy's CLI answers from a cached
daemon and will report an empty graph while a real subscriber is receiving at 33 Hz. Use
`--no-daemon`, or subscribe with `rclpy`.

The fastest true test is two throwaway processes — one publishing, one subscribing, both under
`env -i` with Foxy alone. If they cannot exchange messages, nothing else on this host will work.
