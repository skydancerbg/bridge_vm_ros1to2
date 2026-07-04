# Continuation Checklist

Use this checklist when starting from a new VM or new agent session.

## Access

- [ ] Confirm SSH to `swu@10.25.25.107`.
- [ ] Confirm passwordless sudo or root path on `10.25.25.107`.
- [ ] Confirm SSH to `swu@10.25.25.115`.
- [ ] Confirm `root@10.25.25.115` if deeper sim control is needed.
- [ ] Confirm SSH to `user@10.25.25.113`.
- [ ] Confirm passwordless sudo or root path on `10.25.25.113`.

## Bridge VM Baseline

- [ ] Check `ip -4 addr show`.
- [ ] Check `systemctl status ros-map-export.service`.
- [ ] Check `systemctl status ros1-dynamic-bridge.service`.
- [ ] Check `systemctl status rosbridge-websocket.service`.
- [ ] Check `systemctl status rosbridge-topic-advertiser.service`.
- [ ] Confirm `ros-bridge.service` remains masked.
- [ ] Check `ss -ltnp | grep -E ':8081|:9090'`.

## HTTP Map

- [ ] `curl http://127.0.0.1:8081/`.
- [ ] `curl http://127.0.0.1:8081/map_meta.json`.
- [ ] `curl -I http://127.0.0.1:8081/map.png`.
- [ ] After ROS 1 is reachable, `curl http://127.0.0.1:8081/refresh`.
- [ ] Confirm `generated_at` updates after sim restart.

## ROS 1

- [ ] Set `ROS_MASTER_URI=http://10.25.25.115:11311`.
- [ ] Source Noetic.
- [ ] Check `/robot/static_map`.
- [ ] Check `/robot/amcl_pose`.
- [ ] Check `/robot/robotnik_base_control/odom`.

## ROS 2

- [ ] Source Foxy in ROS 2-only shell.
- [ ] Check `/robot/amcl_pose`.
- [ ] Check `/robot/robotnik_base_control/odom`.
- [ ] Check websocket path if frontend issues remain.

## Documentation

- [ ] Update `/home/swu/obsidian`.
- [ ] Update `/home/swu/bridge-vm-config-repo/docs`.
- [ ] Update `/home/swu/bridge-docs` if root access is available.
- [ ] Run `snapshot_from_live.sh`.
- [ ] Review and commit super repo changes if appropriate.
