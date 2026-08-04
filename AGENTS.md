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
- Websocket endpoint: `ws://10.25.25.108:9090`
- Static map PNG: `http://10.25.25.108:8081/map.png`
- Static map metadata: `http://10.25.25.108:8081/map_meta.json`
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
- Map export is back on the full map extent; current metadata is `4992 x 4992` with the full-map origin.
- Treat the split bridge services as authoritative; `ros-bridge.service` is retired.
- If frontend pose delivery is questioned, compare `/robot/amcl_pose` with `/robot/robotnik_base_control/odom`.
- The current watchdog policy only restarts `ros1-dynamic-bridge.service` when ROS 1 odom publisher visibility is missing and ROS 2 bridged odom is also unhealthy for 3 consecutive checks.
- Bridge-side repeatable nav testing lives in `scripts/capture_nav_goals_ros1.py`, `scripts/run_nav_goal_test_ros1.py`, `scripts/run_nav_goal_test.sh`, `scripts/cancel_nav_goal_test.sh`, and `scripts/nav_goal_test_status.sh`.
- Passwordless SSH from this VM to the sim VM is confirmed for `swu@10.25.25.115` and `root@10.25.25.115`.
- The confirmed remote sim restart entrypoint is `/home/swu/restart_neo_workshop_navigation.sh` on `10.25.25.115`.
- The previous sim terminal can remain hung after a restart; clear it with `Ctrl-C` or close/kill that terminal before assuming the restart path is broken.

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
