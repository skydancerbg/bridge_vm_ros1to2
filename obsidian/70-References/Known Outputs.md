# Known Outputs

## Map Exporter Index

Command:

```bash
curl http://127.0.0.1:8081/
```

Observed output:

```json
{"endpoints":["/","/refresh","/map.png","/map_meta.json"],"map_service":"/robot/static_map","service":"ros-map-export"}
```

## Map Metadata

Command:

```bash
curl http://127.0.0.1:8081/map_meta.json
```

Observed output:

```json
{
  "resolution": 0.019999999552965164,
  "width": 4992,
  "height": 4992,
  "origin": {
    "position": {
      "x": -50.0,
      "y": -50.0,
      "z": 0.0
    },
    "orientation": {
      "qx": 0.0,
      "qy": 0.0,
      "qz": 0.0,
      "qw": 1.0
    }
  },
  "generated_at": "2026-07-04T02:20:06.529605+00:00",
  "image": "/map.png"
}
```

## Map PNG HEAD

Command:

```bash
curl -I http://127.0.0.1:8081/map.png
```

Observed:
- `HTTP/1.0 200 OK`
- `Content-Type: image/png`
- `Content-Length: 39658`

## ROS 1 Master Failure

Command:

```bash
rosservice info /robot/static_map
```

Observed while upstream was down:

```text
ERROR: Unable to communicate with master!
```

## ROS 1 Master Restored

After the user started the simulation/ROS master on `2026-07-04`, `/robot/static_map` was reachable:

```text
Node: /robot/robot_map_server
URI: rosrpc://10.25.25.115:58229
Type: nav_msgs/GetMap
Args:
```

Map refresh succeeded:

```json
{"meta":{"generated_at":"2026-07-04T02:20:06.529605+00:00","height":4992,"image":"/map.png","origin":{"orientation":{"qw":1.0,"qx":0.0,"qy":0.0,"qz":0.0},"position":{"x":-50.0,"y":-50.0,"z":0.0}},"resolution":0.019999999552965164,"width":4992},"status":"ok"}
```

## Dynamic Bridge Logs During Upstream Failure

Observed repeated messages:

```text
Error in XmlRpcClient::writeRequest: write error (Connection refused).
Error in XmlRpcDispatch::work: couldn't find source iterator
```
