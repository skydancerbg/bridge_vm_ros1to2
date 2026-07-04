# Topics and Data Contracts

## Frontend HTTP Map Contract

Map PNG:
- URL: `http://10.25.25.107:8081/map.png`
- Content type: `image/png`
- Current cached size: `4992 x 4992`
- Encoding: 8-bit grayscale PNG
- Orientation: vertically flipped for browser display

Map metadata:
- URL: `http://10.25.25.107:8081/map_meta.json`

Required fields:
- `resolution`
- `width`
- `height`
- `origin.position.x`
- `origin.position.y`
- `origin.position.z`
- `origin.orientation.qx`
- `origin.orientation.qy`
- `origin.orientation.qz`
- `origin.orientation.qw`
- `generated_at`
- `image`

## Frontend Websocket Contract

Websocket:
- `ws://10.25.25.107:9090`

Preferred pose topic:
- `/robot/amcl_pose`
- Type: `geometry_msgs/msg/PoseWithCovarianceStamped`

Diagnostic/fallback motion topic:
- `/robot/robotnik_base_control/odom`
- Type: `nav_msgs/msg/Odometry`

## ROS 1 Service Contract

Map source:
- `/robot/static_map`
- Type: `nav_msgs/GetMap`
- Available only when ROS 1 master at `10.25.25.115:11311` is reachable and map server is active.

## Current Warning

Do not make the frontend depend on ROS 1 master, ROS 1 service types, or direct ROS 1 endpoints. The bridge VM owns that translation.

Future Robot Control Center web app VM:
- LAN: `10.10.25.113`
- Tailscale: `100.121.18.83`
- Should consume bridge VM endpoints, not ROS 1 directly.
