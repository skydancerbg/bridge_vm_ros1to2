# ros1-dynamic-bridge.service

## Purpose

Runs ROS 1 -> ROS 2 dynamic bridging for topics.

## Live Unit

Path:
- `/etc/systemd/system/ros1-dynamic-bridge.service`

Service properties:
- `User=swu`
- `WorkingDirectory=/home/swu`
- `ExecStart=/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`
- `Restart=always`

## Watchdog Script

Path:
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`

Behavior:
- Sets `ROS_MASTER_URI=http://10.25.25.115:11311`.
- Sets `ROS_IP=10.25.25.107`.
- Sources Noetic then Foxy.
- Starts `ros2 run ros1_bridge dynamic_bridge --bridge-all-topics`.
- Checks ROS 1 odom publisher health.
- Checks ROS 2 bridged odom health.
- Restarts via systemd only after sustained combined failures.

## Current Observed Issue

On `2026-07-04`, service was active but logs showed repeated XML-RPC connection refused errors. This points to upstream ROS 1 master at `10.25.25.115:11311` being unavailable.

## Verify

```bash
systemctl status ros1-dynamic-bridge.service --no-pager -l
ps -ef | grep dynamic_bridge | grep -v grep
journalctl -u ros1-dynamic-bridge.service -n 80 --no-pager -l
```

ROS 1 check:

```bash
unset ROS_HOSTNAME
export ROS_MASTER_URI=http://10.25.25.115:11311
export ROS_IP=10.25.25.107
source /opt/ros/noetic/setup.bash
rostopic info /robot/robotnik_base_control/odom
```

ROS 2 check:

```bash
unset ROS_MASTER_URI ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION ROS_DISTRO ROS_HOSTNAME
export ROS_IP=10.25.25.107
export ROS_LOCALHOST_ONLY=0
source /opt/ros/foxy/setup.bash
ros2 topic list -t | grep /robot/robotnik_base_control/odom
```

## Related Notes

- [[60-Decisions/Split Bridge Services]]
- [[40-Operations/Recovery Playbooks]]

