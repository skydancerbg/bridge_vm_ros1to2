# ros-map-export.service

## Purpose

Serves the static map and metadata to the frontend over HTTP on port `8081`.

## Live Unit

Path:
- `/etc/systemd/system/ros-map-export.service`

Service properties:
- `User=swu`
- `WorkingDirectory=/home/swu/map_exporter`
- `ExecStart=/home/swu/map_exporter/run.sh`
- `Restart=always`

## Application Files

Live files:
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`
- `/home/swu/map_exporter/output/map.png`
- `/home/swu/map_exporter/output/map_meta.json`

## Endpoints

- `/`
- `/refresh`
- `/map.png`
- `/map_meta.json`

## Behavior

`app.py`:
- Uses ROS 1 Noetic via `rospy`.
- Calls `/robot/static_map` via `nav_msgs/GetMap`.
- Converts `nav_msgs/OccupancyGrid` into grayscale PNG.
- Vertically flips the image for browser display.
- Writes `map.png` and `map_meta.json`.
- Binds Flask to `0.0.0.0:8081`.
- Starts the initial refresh in a background thread so cached map files can serve even if ROS 1 is unavailable.
- Makes `/refresh` nonblocking against an existing refresh lock.

`run.sh`:
- Unsets `ROS_HOSTNAME`.
- Sets `ROS_MASTER_URI=http://10.25.25.115:11311`.
- Sets `ROS_IP` from `hostname -I`.
- Sources `/opt/ros/noetic/setup.bash`.
- Enables strict shell mode after sourcing Noetic.
- Executes `python3 /home/swu/map_exporter/app.py`.

Important shell decision:
- Do not put `set -u` before sourcing Noetic. Noetic setup scripts can reference unset variables.

## Current Map Contract

Metadata fields:
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

## Current Known Limitation

If `10.25.25.115:11311` is down, `/refresh` cannot complete. Cached `/map.png` and `/map_meta.json` can still serve.

## Verify

```bash
systemctl status ros-map-export.service --no-pager -l
curl -sS http://127.0.0.1:8081/
curl -sS http://127.0.0.1:8081/map_meta.json
curl -I http://127.0.0.1:8081/map.png
```

## Related Notes

- [[60-Decisions/HTTP Map Export Instead Of Rosbridge]]
- [[40-Operations/Recovery Playbooks]]

