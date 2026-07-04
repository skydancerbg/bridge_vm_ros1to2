# Verification Commands

Run these from the bridge VM unless noted otherwise.

## Service State

```bash
systemctl status ros-map-export.service --no-pager -l
systemctl status ros1-dynamic-bridge.service --no-pager -l
systemctl status rosbridge-websocket.service --no-pager -l
systemctl status rosbridge-topic-advertiser.service --no-pager -l
systemctl status ros-bridge.service --no-pager -l || true
```

Expected:
- First four services active.
- `ros-bridge.service` masked/inactive.

## Ports

```bash
ss -ltnp | grep -E ':8081|:9090'
```

Expected:
- `0.0.0.0:8081` owned by `python3 /home/swu/map_exporter/app.py`.
- `0.0.0.0:9090` owned by rosbridge websocket.

## Map Exporter

```bash
curl -sS http://127.0.0.1:8081/
curl -sS http://127.0.0.1:8081/map_meta.json
curl -I http://127.0.0.1:8081/map.png
curl -i http://127.0.0.1:8081/refresh
```

Interpretation:
- `/`, `/map_meta.json`, and `/map.png` should respond even if ROS 1 is unavailable, as long as cached files exist.
- `/refresh` needs upstream ROS 1 master and `/robot/static_map`.
- `202 busy` means a refresh call is already in progress or stuck behind ROS connectivity.

## ROS 1 Master

```bash
unset ROS_HOSTNAME
export ROS_MASTER_URI=http://10.25.25.115:11311
export ROS_IP=10.25.25.107
source /opt/ros/noetic/setup.bash
rosservice info /robot/static_map
rostopic info /robot/amcl_pose
rostopic info /robot/robotnik_base_control/odom
```

If this returns `ERROR: Unable to communicate with master!`, fix the upstream sim/ROS 1 VM first.

## ROS 2 Topic Graph

```bash
unset ROS_MASTER_URI ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION ROS_DISTRO ROS_HOSTNAME
export ROS_IP=10.25.25.107
export ROS_LOCALHOST_ONLY=0
source /opt/ros/foxy/setup.bash
ros2 topic list -t | egrep '/robot/amcl_pose|/robot/robotnik_base_control/odom'
```

## Super Repo Verification

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/verify_live_state.sh
```

## Network

```bash
ip -4 addr show
ip route
ping -c 3 10.25.25.115
nc -vz 10.25.25.115 11311
```

`nc` may not be installed. Use `timeout 5 bash -lc '</dev/tcp/10.25.25.115/11311'` as an alternative.

## Related Notes

- [[40-Operations/Recovery Playbooks]]
- [[20-Infrastructure/Machines and Access]]

