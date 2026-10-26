# Current Status

Updated 2026-10-27. The sections below this block are the July 2026 observation and are historical; addresses changed, see [[Project Infrastructure 2026-10]] and [[Address change 2026-10-26]].

- Phases 0-1 of the web control center are done; Phase 2: P2.1-P2.5 done, P2.6 (technician mobile view) next.
- Bridge: rosbridge :9090 and map exporter :8081 on 10.25.25.115, supervised by rosbridge-health.service; ROS master is the sim VM 10.25.25.123.
- Regression suite on the web VM: 30/30 green.
- Map is drawn white by default (dark is an opt-in); the robot marker shows on page open.

---

## Last Observed

Observed on `2026-07-04` from bridge VM `ros1ros2bridge`.

## Service State

Active:
- `ros-map-export.service`
- `ros1-dynamic-bridge.service`
- `rosbridge-websocket.service`
- `rosbridge-topic-advertiser.service`

Masked/retired:
- `ros-bridge.service`

## Endpoint State

Expected active endpoints:
- `http://10.25.25.107:8081/`
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`
- `ws://10.25.25.107:9090`

Map exporter status:
- The HTTP service is active.
- Full-map files are available.
- `/refresh` succeeded after the user started the simulation/ROS master on `2026-07-04`.

## ROS 1 Master Status

The upstream ROS 1 master at `http://10.25.25.115:11311` was unreachable on `2026-07-03`, with direct checks returning:

```text
ERROR: Unable to communicate with master!
```

The user started the simulation/ROS master on the sim VM on `2026-07-04`. After that:
- `/robot/static_map` was reachable from the bridge VM.
- `curl http://127.0.0.1:8081/refresh` succeeded.
- `generated_at` updated to `2026-07-04T02:20:06.529605+00:00`.

## Current Map Metadata

The metadata currently served by the map exporter:
- Resolution: `0.019999999552965164`
- Width: `4992`
- Height: `4992`
- Origin position: `x=-50.0`, `y=-50.0`, `z=0.0`
- Origin orientation: `qx=0.0`, `qy=0.0`, `qz=0.0`, `qw=1.0`
- Image path: `/map.png`
- Latest generated timestamp observed after refresh: `2026-07-04T02:20:06.529605+00:00`

## Next Immediate Actions

1. Keep ROS 1 master reachability stable at `10.25.25.115:11311`.
2. Revalidate websocket delivery of `/robot/amcl_pose`.
3. Keep the sim start command documented and validate it after sim VM changes.
4. Prepare future Robot Control Center web app work on VM `12850`.

## Related Notes

- [[20-Infrastructure/Machines and Access]]
- [[20-Infrastructure/Web App VM 10.25.25.113]]
- [[30-Services/ros-map-export.service]]
- [[30-Services/ros1-dynamic-bridge.service]]
- [[40-Operations/Verification Commands]]
