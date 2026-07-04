# Agent Quickstart

## Mission

Continue development and operation of the ROS bridge project without breaking the current split-service architecture.

The bridge VM is `10.25.25.107`. The upstream ROS 1 master/sim VM is `10.25.25.115`. The future Robot Control Center web app VM is `10.25.25.113`.

Proxmox:
- Server/node: `aipve`
- Bridge VM: ID `12800`, `u20-ROS1ROS2-bridge`
- Sim/ROS 1 VM: ID `12851`, `u20-RB1sim-ros1and2-bridge-geminicli`
- Web app VM: ID `12850`, `u24ai-RobcoGADGET-web`

## First Commands To Run

```bash
hostname
ip -4 addr show
systemctl status ros-map-export.service --no-pager -l
systemctl status ros1-dynamic-bridge.service --no-pager -l
systemctl status rosbridge-websocket.service --no-pager -l
systemctl status rosbridge-topic-advertiser.service --no-pager -l
systemctl status ros-bridge.service --no-pager -l || true
curl -sS http://127.0.0.1:8081/map_meta.json
ss -ltnp | grep -E ':8081|:9090'
```

## Expected Baseline

Expected:
- `ros-map-export.service` active.
- `ros1-dynamic-bridge.service` active.
- `rosbridge-websocket.service` active.
- `rosbridge-topic-advertiser.service` active.
- `ros-bridge.service` masked/inactive.
- `8081` listening.
- `9090` listening.

Latest ROS 1 status:
- Upstream ROS 1 master was down on `2026-07-03`.
- The user started the simulation/ROS master on `2026-07-04`.
- `/robot/static_map` was reachable and map refresh succeeded after that.

## Do Not Do

Do not:
- Revive `ros-bridge.service`.
- Move websocket off `9090`.
- Move map export off `8081`.
- Send full map payloads through rosbridge.
- Edit backup folders as source of truth.
- Edit `bridge-vm-config-repo/live-files` as primary source.
- Source Noetic into `rosbridge-websocket.service`.

## Safe Places To Edit

Live source paths:
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`
- `/home/swu/bridge_support/ros2_topic_advertiser.py`
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`
- `/etc/systemd/system/*.service`

Documentation:
- `/home/swu/obsidian`
- `/home/swu/bridge-vm-config-repo/docs`
- `/home/swu/bridge-docs` if root access is available

## After Any Live Change

```bash
sudo systemctl daemon-reload
sudo systemctl restart <changed-service>
systemctl status <changed-service> --no-pager -l
cd /home/swu/bridge-vm-config-repo
./scripts/snapshot_from_live.sh
git status --short
```

## Current Development Priorities

1. Keep upstream ROS 1 master stable at `10.25.25.115:11311`.
2. Revalidate `/robot/amcl_pose` over websocket.
3. Use the documented sim start command if ROS master is down.
4. Prepare future web app work on `10.25.25.113`.
5. Keep frontend using HTTP map plus websocket live topics.
6. Keep docs and vault updated.

## Important Linked Notes

- [[00-Start/Current Status]]
- [[10-Architecture/Runtime Architecture]]
- [[20-Infrastructure/Machines and Access]]
- [[30-Services/Service Inventory]]
- [[40-Operations/Verification Commands]]
- [[40-Operations/Recovery Playbooks]]
- [[50-Development/Super Repo Workflow]]
- [[60-Decisions/Decision Log]]
