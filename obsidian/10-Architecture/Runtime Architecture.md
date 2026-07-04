# Runtime Architecture

## Summary

The current architecture separates heavy static map delivery from live robot telemetry:

```text
ROS 1 sim/master on 10.25.25.115
  |
  | ROS 1 XML-RPC / topics / services
  v
Bridge VM 10.25.25.107
  |
  | ros1_bridge dynamic_bridge
  v
ROS 2 Foxy graph
  |
  | rosbridge websocket
  v
Frontend websocket clients on ws://10.25.25.107:9090

Bridge VM map exporter
  |
  | ROS 1 /robot/static_map via nav_msgs/GetMap
  v
PNG + JSON files
  |
  | Flask HTTP
  v
Frontend HTTP clients on http://10.25.25.107:8081
```

## Service Split

The bridge runtime is split into separate services:
- [[30-Services/ros1-dynamic-bridge.service]]
- [[30-Services/rosbridge-websocket.service]]
- [[30-Services/rosbridge-topic-advertiser.service]]
- [[30-Services/ros-map-export.service]]

This split replaced the older combined `ros-bridge.service`.

## Important Boundaries

ROS 1 dependency boundary:
- Only the dynamic bridge and map exporter need the upstream ROS 1 master.
- The frontend does not talk to ROS 1 directly.

ROS 2 websocket boundary:
- `rosbridge-websocket.service` runs in ROS 2-only environment.
- This is important for DDS discovery and type behavior.

HTTP map boundary:
- Browser map reads use PNG and JSON over HTTP.
- Large map payloads should not be sent through rosbridge.

## Data Contracts

Frontend map contract:
- `GET /map.png` returns grayscale PNG.
- `GET /map_meta.json` returns resolution, size, origin pose, generated timestamp, and image path.

Frontend live topic contract:
- Connect to `ws://10.25.25.107:9090`.
- Subscribe to `/robot/amcl_pose` for preferred pose.
- Use `/robot/robotnik_base_control/odom` only as fallback or diagnostic if AMCL is sparse.

## Related Notes

- [[60-Decisions/Decision Log]]
- [[50-Development/What Was Developed]]
- [[40-Operations/Verification Commands]]

