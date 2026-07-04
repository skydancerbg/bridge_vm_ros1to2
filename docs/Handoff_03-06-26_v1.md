# Bridge VM Handoff 03-06-26 v1

## Purpose

This is the comprehensive handoff for continuing development from another VM with passwordless access to the bridge VM and the upstream simulation/ROS 1 VM.

The project goal is to keep live/light ROS topics available to the frontend through the existing websocket bridge, while serving large static map artifacts through a reliable HTTP service. The frontend should remain decoupled from ROS 1 implementation details.

This copy is staged in the writable super repo because `/home/swu/bridge-docs` is currently owned by `root` and this session does not have passwordless sudo. Install it to the requested authoritative path with:

```bash
sudo install -o root -g root -m 0644 /home/swu/bridge-vm-config-repo/docs/Handoff_03-06-26_v1.md /home/swu/bridge-docs/Handoff_03-06-26_v1.md
```

## Machine Inventory

| Role | Host/IP | Notes |
| --- | --- | --- |
| Proxmox server/node | `aipve` | Hosts the known project VMs. |
| Bridge VM | `10.25.25.107` | Proxmox VM ID `12800`, name `u20-ROS1ROS2-bridge`; Ubuntu bridge VM `ros1ros2bridge`; runs ROS 1 Noetic, ROS 2 Foxy, dynamic bridge, rosbridge websocket, and HTTP map exporter. |
| Bridge VM Tailscale | `100.102.124.43` | Tailscale address observed on `tailscale0`. |
| Upstream sim / ROS 1 master VM | `10.25.25.115` | Proxmox VM ID `12851`, name `u20-RB1sim-ros1and2-bridge-geminicli`; provides ROS 1 master at `http://10.25.25.115:11311`; expected to host the simulation/navigation stack. |
| Upstream sim Tailscale | `100.79.246.33` | Tailscale address supplied on `2026-07-04`. |
| Future Robot Control Center web app VM | `10.25.25.113` | Proxmox VM ID `12850`, name `u24ai-RobcoGADGET-web`; future web app development target on node `aipve`. |
| Future web app Tailscale | `100.121.18.83` | Tailscale address supplied on `2026-07-04`. |
| Localhost | `127.0.0.1` | Used for bridge-local endpoint checks. |
| Bind-all interfaces | `0.0.0.0` | Used by Flask map exporter and rosbridge websocket listeners. |

## Passwordless Access Needed From A New Development VM

Give the new development VM passwordless SSH access to:
- `swu@10.25.25.107` for normal bridge VM development.
- A sudo-capable path on `10.25.25.107`, ideally passwordless sudo for `systemctl`, `/etc/systemd/system`, `/usr/local/bin`, and package installs.
- `swu@10.25.25.115` for upstream sim status and restart workflows.
- `root@10.25.25.115` if the new VM must reproduce deeper remote access previously confirmed from the bridge VM.
- `user@10.25.25.113` for future Robot Control Center web app development.
- A sudo-capable path on `10.25.25.113` for future web app runtime/deployment work.

Known bridge-side helper scripts assume SSH to `10.25.25.115` through local user `swu`, with optional `SIM_HOST`, `SIM_USER`, and `LOCAL_SSH_USER` environment overrides.

## Ports And Endpoints

| Port | Endpoint | Owner | Purpose |
| --- | --- | --- | --- |
| `8081` | `http://10.25.25.107:8081/` | `ros-map-export.service` | HTTP map exporter index. |
| `8081` | `http://10.25.25.107:8081/map.png` | `ros-map-export.service` | Browser-consumable static map PNG. |
| `8081` | `http://10.25.25.107:8081/map_meta.json` | `ros-map-export.service` | Browser-consumable static map metadata. |
| `8081` | `http://10.25.25.107:8081/refresh` | `ros-map-export.service` | Attempts live refresh from ROS 1 `/robot/static_map`. |
| `9090` | `ws://10.25.25.107:9090` | `rosbridge-websocket.service` | Websocket bridge for frontend live/light ROS topics. |
| `11311` | `http://10.25.25.115:11311` | upstream ROS 1 master | ROS 1 master used by bridge and map exporter. |

Frontend should use:
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`
- `ws://10.25.25.107:9090` for `/robot/amcl_pose`

## Software Installed On The Bridge VM

Confirmed packages on `10.25.25.107`:
- ROS 1 Noetic desktop full: `ros-noetic-desktop-full 1.5.0-1focal.20250521.014741`
- ROS 2 Foxy base: `ros-foxy-ros-base 0.9.2-1focal.20230606.035837`
- ROS 1 bridge: `ros-foxy-ros1-bridge 0.9.7-1focal.20230527.055419`
- ROS 2 rosbridge server: `ros-foxy-rosbridge-server 1.3.1-1focal.20230527.054025`
- Flask: `python3-flask 1.1.1-2ubuntu0.1`
- Pillow/PIL: `python3-pil 7.0.0-4ubuntu0.9`
- Tailscale: `tailscale 1.98.4`

Observed local tools and services:
- `systemd`
- `curl`
- `ss`
- `git`
- `rg`
- `python3`
- ROS CLI tools from Noetic and Foxy.

Software on `10.25.25.115` was not inspected in the current session because ROS master was unreachable. Existing docs and scripts assume it runs the ROS 1 simulation/navigation stack and has `/home/swu/restart_neo_workshop_navigation.sh`.

## Current Project Status

As of `2026-07-04`:
- `ros-map-export.service` is active and serving full-map files on `8081`.
- `ros1-dynamic-bridge.service` is active and runs the ROS 1 -> ROS 2 dynamic bridge through a watchdog wrapper.
- `rosbridge-websocket.service` is active and listening on `0.0.0.0:9090`.
- `rosbridge-topic-advertiser.service` is active and advertises important ROS 2 topic types for rosbridge.
- Legacy `ros-bridge.service` is masked/retired.
- `ROS_MASTER_URI=http://10.25.25.115:11311` was unreachable from the bridge VM on `2026-07-03`.
- The user started the simulation/ROS master on `10.25.25.115` on `2026-07-04`.
- `/robot/static_map` was reachable from the bridge VM on `2026-07-04`.
- `curl http://127.0.0.1:8081/refresh` succeeded on `2026-07-04`.

Current map metadata being served:
- Resolution: `0.019999999552965164`
- Width: `4992`
- Height: `4992`
- Origin position: `x=-50.0`, `y=-50.0`, `z=0.0`
- Origin orientation: `qx=0.0`, `qy=0.0`, `qz=0.0`, `qw=1.0`
- Image path: `/map.png`
- Latest generated timestamp observed after refresh: `2026-07-04T02:20:06.529605+00:00`

## Current Stage

The project is in stabilization and handoff stage. The runtime architecture is considered the current intended path:
- Split dynamic bridge service for ROS 1 -> ROS 2.
- Separate ROS 2-only rosbridge websocket service for browser websocket access.
- Separate HTTP map export service for static map delivery.
- Super repo mirror/tooling for reproducible bridge VM maintenance.

The next developer should avoid architecture rewrites until upstream ROS 1 master reachability and frontend pose behavior have been revalidated.

## Live Services

### `ros1-dynamic-bridge.service`

Purpose:
- Runs ROS 1 -> ROS 2 `dynamic_bridge --bridge-all-topics`.
- Uses `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`.

Important details:
- Sources ROS 1 Noetic then ROS 2 Foxy.
- Uses `ROS_MASTER_URI=http://10.25.25.115:11311`.
- Uses `ROS_IP=10.25.25.107`.
- Watchdog avoids restart loops when upstream ROS 1 publishers are temporarily absent.

Key files:
- `/etc/systemd/system/ros1-dynamic-bridge.service`
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`

### `rosbridge-websocket.service`

Purpose:
- Exposes ROS 2 topics to websocket clients on `0.0.0.0:9090`.

Important details:
- Runs in a ROS 2-only environment.
- Explicitly unsets ROS 1 environment variables.
- Uses `max_message_size:=100000000`.

Key file:
- `/etc/systemd/system/rosbridge-websocket.service`

### `rosbridge-topic-advertiser.service`

Purpose:
- Keeps important topic names/types visible in ROS 2 so rosbridge can resolve browser subscriptions.

Topics advertised:
- `/robot/robotnik_base_control/odom` as `nav_msgs/msg/Odometry`
- `/robot/amcl_pose` as `geometry_msgs/msg/PoseWithCovarianceStamped`

Key files:
- `/etc/systemd/system/rosbridge-topic-advertiser.service`
- `/home/swu/bridge_support/ros2_topic_advertiser.py`

### `ros-map-export.service`

Purpose:
- Calls ROS 1 `/robot/static_map` using `nav_msgs/GetMap`.
- Converts OccupancyGrid values into grayscale PNG.
- Vertically flips the image for browser display.
- Writes and serves `/home/swu/map_exporter/output/map.png` and `/home/swu/map_exporter/output/map_meta.json`.

Endpoints:
- `/`
- `/refresh`
- `/map.png`
- `/map_meta.json`

Important behavior:
- Flask binds immediately on startup.
- Initial map refresh runs in a background thread so HTTP serving does not block if ROS 1 is unavailable.
- `/refresh` is nonblocking with respect to an existing refresh lock; it returns `202` busy instead of hanging behind a stuck ROS call.

Key files:
- `/etc/systemd/system/ros-map-export.service`
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`

### `ros-bridge.service`

Purpose:
- Legacy combined bridge service retained only as a guardrail/reference.

Current state:
- Masked/retired.
- Do not revive it unless deliberately rolling back from split services.

Related files:
- `/etc/systemd/system/ros-bridge.service`
- `/etc/systemd/system/ros-bridge.service.legacy-disabled`
- `/etc/systemd/system/ros-bridge.service.retired`
- `/usr/local/bin/bridge_startup.sh`

## The Super Repo

Path:
- `/home/swu/bridge-vm-config-repo`

Purpose:
- Git-ready mirror of important bridge VM live files.
- Restore/rebuild toolkit.
- Documentation and handoff bundle.
- Commit-time snapshot workspace.

How it works:
- Live OS files remain authoritative.
- Mirrored copies live under `/home/swu/bridge-vm-config-repo/live-files`.
- `MANIFEST/files_manifest.yaml` lists live files and mirror destinations.
- `MANIFEST/services_manifest.yaml` describes services, verification commands, and restart commands.
- `scripts/snapshot_from_live.sh` copies live files into the repo mirror and updates permissions metadata.
- `scripts/restore_to_live.sh` restores mirrored files back into live OS paths.
- `scripts/verify_live_state.sh` checks key service and endpoint state.
- `scripts/prepare_commit_snapshot.sh` prepares a commit snapshot.

Use pattern:
1. Make changes in live paths.
2. Verify services and endpoints.
3. Run `/home/swu/bridge-vm-config-repo/scripts/snapshot_from_live.sh`.
4. Review `git diff` in `/home/swu/bridge-vm-config-repo`.
5. Commit from the super repo if the change is valid.

GitHub:
- Repository: `skydancerbg/bridge_vm_ros1to2`
- SSH remote: `git@github.com:skydancerbg/bridge_vm_ros1to2.git`
- Deploy-key SSH auth is working from this bridge VM.
- Verify with `ssh -o BatchMode=yes -T git@github.com`.
- Push with `cd /home/swu/bridge-vm-config-repo && git push origin main`.
- See `/home/swu/obsidian/40-Operations/set_GitHub_for_the_project.md`.

## Main Project Folders

| Path | Purpose |
| --- | --- |
| `/home/swu/bridge-docs` | Live handoff and operator documentation. Currently root-owned. |
| `/home/swu/bridge-vm-config-repo` | Git-ready super repo/mirror/toolkit. |
| `/home/swu/bridge-vm-config-repo/live-files` | Mirrored copies of selected live OS files. |
| `/home/swu/bridge-vm-config-repo/MANIFEST` | File and service manifests used by repo scripts. |
| `/home/swu/bridge-vm-config-repo/scripts` | Verification, snapshot, restore, remote sim, and nav-test helpers. |
| `/home/swu/bridge-vm-config-repo/docs` | Historical and current bridge documentation. |
| `/home/swu/bridge-backups` | Older stage backups and rollback material. |
| `/home/swu/map_exporter` | Live HTTP map exporter application. |
| `/home/swu/map_exporter/output` | Generated `map.png` and `map_meta.json`. |
| `/home/swu/bridge_support` | Small live helper scripts such as ROS 2 topic advertiser. |
| `/usr/local/bin` | Live bridge startup/watchdog scripts. |
| `/etc/systemd/system` | Live systemd units. |

## Current Development Decisions And Why

Static maps use HTTP, not rosbridge:
- Large map delivery through rosbridge/browser was unreliable. The map is exported to PNG plus JSON metadata and served through Flask on `8081`.

Live/light topics stay on websocket:
- The existing websocket workflow already worked for live/light topics. Keeping it on `9090` avoids unnecessary frontend churn.

Bridge services are split:
- Dynamic bridge, websocket, type advertiser, and map exporter have separate restart/failure boundaries.

Rosbridge runs ROS 2-only:
- The websocket service explicitly unsets ROS 1 variables before sourcing Foxy to avoid mixed-environment discovery/type problems.

Topic advertiser exists for type inference:
- Advertising `/robot/amcl_pose` and `/robot/robotnik_base_control/odom` into ROS 2 makes browser subscriptions resolvable.

Dynamic bridge uses a watchdog:
- The watchdog restarts only after sustained evidence of trouble instead of bouncing on short upstream publisher gaps.

Map exporter starts HTTP before refresh completes:
- Cached `/map.png` and `/map_meta.json` remain available even when ROS 1 is unavailable.

## Paths To Avoid Or Treat Carefully

Avoid editing these as primary development paths:
- `/home/swu/bridge-backups/*`: historical backups only.
- `/home/swu/bridge-vm-config-repo/old-backups/*`: archived rollback snapshots only.
- `/home/swu/bridge-vm-config-repo/live-files/*` directly: mirror only; edit live paths first, then snapshot.
- `/etc/systemd/system/ros-bridge.service`: legacy masked combined service, not the current runtime.
- `/usr/local/bin/bridge_startup.sh`: legacy combined startup wrapper, retained for reference/rollback.
- `/home/swu/.cache`, `/home/swu/.config`, `/home/swu/.ros/log`: runtime/user state, not project source.

Treat these with care:
- `/etc/systemd/system/*`: live service definitions; run `systemctl daemon-reload` after unit edits.
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`: live dynamic bridge watchdog; mistakes can take down ROS 1 -> ROS 2 forwarding.
- `/home/swu/map_exporter/app.py`: live HTTP endpoint implementation; verify with `curl` after edits.
- `/home/swu/map_exporter/run.sh`: environment setup for ROS 1 Noetic; keep ROS setup before strict `set -u`.

## Verification Commands

Run on bridge VM:

```bash
systemctl status ros1-dynamic-bridge.service --no-pager -l
systemctl status rosbridge-websocket.service --no-pager -l
systemctl status rosbridge-topic-advertiser.service --no-pager -l
systemctl status ros-map-export.service --no-pager -l
systemctl status ros-bridge.service --no-pager -l || true
ss -ltnp | grep -E ':8081|:9090'
curl -sS http://127.0.0.1:8081/
curl -sS http://127.0.0.1:8081/map_meta.json
curl -I http://127.0.0.1:8081/map.png
```

Check ROS 1 master:

```bash
unset ROS_HOSTNAME
export ROS_MASTER_URI=http://10.25.25.115:11311
export ROS_IP=10.25.25.107
source /opt/ros/noetic/setup.bash
rosservice info /robot/static_map
rostopic info /robot/amcl_pose
rostopic info /robot/robotnik_base_control/odom
```

Check ROS 2 topics:

```bash
unset ROS_MASTER_URI ROS_ETC_DIR ROS_PACKAGE_PATH ROS_ROOT ROSLISP_PACKAGE_DIRECTORIES ROS_VERSION ROS_DISTRO ROS_HOSTNAME
export ROS_IP=10.25.25.107
export ROS_LOCALHOST_ONLY=0
source /opt/ros/foxy/setup.bash
ros2 topic list -t | egrep '/robot/amcl_pose|/robot/robotnik_base_control/odom'
```

Use super repo verification:

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/verify_live_state.sh
```

## Remote Sim Commands

From the bridge VM:

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/remote_sim_status.sh
./scripts/remote_sim_restart.sh
```

Default remote sim settings:
- `SIM_HOST=10.25.25.115`
- `SIM_USER=swu`
- `LOCAL_SSH_USER=swu`

Remote restart entrypoint expected on sim VM:
- `/home/swu/restart_neo_workshop_navigation.sh`

Confirmed simulation start command on the sim VM:

```bash
cd ~/catkin_ws && source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rb1_base_gazebo rb1_neo_workshop_navigation.launch
```

This starts the simulation and therefore starts ROS master for the bridge VM. Existing project scripts also point to `/home/swu/restart_neo_workshop_navigation.sh` as the known restart/start wrapper.

Known remote sim caution:
- A previous sim launcher terminal can remain hung after restart attempts. Clear it with `Ctrl-C` or close/kill that terminal on the sim VM before assuming bridge recovery is bad.

## Future Robot Control Center Web App VM

Future web app development target:
- Proxmox node/server: `aipve`
- VM ID: `12850`
- VM name: `u24ai-RobcoGADGET-web`
- LAN IP: `10.25.25.113`
- Tailscale IP: `100.121.18.83`

The expected web app role is the future Robot Control Center / RobcoGADGET frontend. It should consume the bridge VM endpoints rather than coupling directly to ROS 1:
- Map PNG: `http://10.25.25.107:8081/map.png`
- Map metadata: `http://10.25.25.107:8081/map_meta.json`
- Live websocket: `ws://10.25.25.107:9090`

## Model Routing For Future Coding Tasks

Use the model-routing guide supplied on `2026-07-04` for future project coding work:
- Default Codex CLI worker: `gpt-5.4`, effort `medium`.
- Cheap Codex CLI worker: `gpt-5.4-mini`, effort `low/medium`, only for bounded docs/tests/simple mechanical work.
- Hard Codex CLI work: `gpt-5.4`, effort `high`.
- Rare Codex escalation/review: `gpt-5.5`, effort `high/xhigh`.
- Default Claude Code worker: `claude-sonnet-5`, effort `medium`.
- Cheap Claude worker: `claude-haiku-4-5`, effort `low/medium`.
- Hard Claude work: `claude-sonnet-5`, effort `high`.
- Rare Claude review/escalation: `claude-opus-4.8` or `claude-fable-5`, effort `high/xhigh`.

Never use cheap models for final decisions on security, money, GDPR/privacy, child safety, production operations, or legal/accounting interpretation. Use top models mainly as reviewers for high-risk work such as RLS, auth, ledger/VAT/refunds, outbound PII, child safety, production deployment, phase exits, and stubborn bugs.

## What Is Left For Development

- Keep upstream ROS 1 master reachability stable from bridge VM to `10.25.25.115:11311`.
- Re-run `curl http://127.0.0.1:8081/refresh` after simulation restarts and confirm `generated_at` updates.
- Revalidate live `/robot/amcl_pose` through websocket.
- If `/robot/amcl_pose` remains sparse, decide whether frontend should temporarily use `/robot/robotnik_base_control/odom` for smoother motion while keeping AMCL as the semantic target.
- Continue frontend smoothing/jumpiness work; previous notes say major hide/reappear collapse was mostly resolved.
- Keep docs and super repo mirror current after each service-level change.
- Optionally replace Flask dev server with a production WSGI server later.

## Known Good Local Outputs

`curl http://127.0.0.1:8081/`:

```json
{"endpoints":["/","/refresh","/map.png","/map_meta.json"],"map_service":"/robot/static_map","service":"ros-map-export"}
```

`curl http://127.0.0.1:8081/map_meta.json`:

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
  "generated_at": "2026-04-11T08:13:51.802536+00:00",
  "image": "/map.png"
}
```

`curl -I http://127.0.0.1:8081/map.png` returned:
- `HTTP/1.0 200 OK`
- `Content-Type: image/png`
- `Content-Length: 39658`

ROS 1 master check on `2026-07-03` returned:

```text
ERROR: Unable to communicate with master!
```

After the sim was started by the user on `2026-07-04`, `/robot/static_map` was reachable:

```text
Node: /robot/robot_map_server
URI: rosrpc://10.25.25.115:58229
Type: nav_msgs/GetMap
Args:
```

Map refresh succeeded on `2026-07-04`:

```json
{"meta":{"generated_at":"2026-07-04T02:20:06.529605+00:00","height":4992,"image":"/map.png","origin":{"orientation":{"qw":1.0,"qx":0.0,"qy":0.0,"qz":0.0},"position":{"x":-50.0,"y":-50.0,"z":0.0}},"resolution":0.019999999552965164,"width":4992},"status":"ok"}
```

## Recovery Rules

- If `8081` is down, check `ros-map-export.service` first, then `/home/swu/map_exporter/app.py` and `/home/swu/map_exporter/run.sh`.
- If `9090` is down, check `rosbridge-websocket.service` and confirm no rogue process owns the port.
- If ROS 2 topics are missing from rosbridge, check `rosbridge-topic-advertiser.service`.
- If ROS 1 -> ROS 2 topics are missing, check `ros1-dynamic-bridge.service`, its watchdog logs, and upstream ROS 1 master reachability.
- If the map is stale but still served, fix ROS 1 master reachability and call `/refresh`.
- Do not unmask or restart `ros-bridge.service` unless intentionally rolling back from split services.
