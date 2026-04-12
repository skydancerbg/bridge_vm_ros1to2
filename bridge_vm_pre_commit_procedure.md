# bridge_vm_pre_commit_procedure.md

## Purpose

This file documents the **current bridge VM pre-commit workflow** for manual execution and includes a **Codex prompt** that follows the same procedure.

This procedure is for the **bridge VM only**.

The repository is a **mirror of scattered live system files**. Live files remain in their real OS locations on the OS. The repo stores mirrored copies, manifests, documentation, and restore information.

For Codex usage, prefer the repo-local skill:

`Use the bridge-precommit-commit skill. Refresh the mirror from live state, verify the bridge runtime, update mirrored docs/manifests, stage the relevant files, and if everything is verified ready, commit with the standard post-fix message.`

---

## Current authoritative baseline

### Repo root
`/home/swu/bridge-vm-config-repo`

### Bridge documentation / handoff area
`/home/swu/bridge-docs`

### Portable backup area
`/home/swu/bridge-backups`

### Authoritative architecture
The **split-service bridge design** is the authoritative baseline:

- `ros1-dynamic-bridge.service`
- `rosbridge-websocket.service`
- `ros-map-export.service`

The legacy combined service must remain **retired / masked / non-authoritative**:

- `ros-bridge.service`

---

## Current working state to preserve

The following is the currently validated working state and should be reflected in repo docs and mirrors before commit:

- Root cause of the missing robot on the map was **stale / rogue runtime ownership around rosbridge on port 9090**
- Resolution:
  - rogue processes were removed
  - managed bridge services were restarted
  - split services remain authoritative
  - legacy `ros-bridge.service` remains masked / retired
- Current validated runtime:
  - port **9090** is owned only by the intended rosbridge process
  - port **8081** is owned by the map exporter
  - `/robot/robotnik_base_control/odom` is live
  - typed websocket subscribe receives odom publish frames
  - the robot is visible and moving in the UI
- Watchdog policy now preserves bridge continuity during navigation:
  - ROS 1 publisher absence alone does **not** force restart
  - restart now requires ROS 1 publisher missing **and** unhealthy ROS 2 bridged odom for **3 consecutive checks**
- Repeatable bridge-side testing helpers now exist for:
  - RViz 2D Nav Goal capture
  - status-driven 4-goal nav runs
  - active-goal cancel
  - current nav-test status
- Remote sim-control workflow is documented and must remain preserved.
- `AMCL` was **not required** for the successful fix
- No rollback is needed

---

## Files that must be tracked in the mirror

At minimum, the mirrored repo should track these live files if they exist and are still relevant:

- `/etc/systemd/system/ros1-dynamic-bridge.service`
- `/etc/systemd/system/rosbridge-websocket.service`
- `/etc/systemd/system/ros-map-export.service`
- `/usr/local/bin/bridge_startup.sh` *(if still relevant)*
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`
- `/home/swu/bridge-docs/AGENTS.md`
- `/home/swu/bridge-docs/PROJECT_STATUS.md`
- `/home/swu/bridge-docs/CURRENT_STAGE.md`

Also review:

- `README.md`
- `MANIFEST/*.yaml`
- restore / backup notes if present
- any repo-specific handoff or pre-commit notes

---

## Manual pre-commit sequence

Run these commands in order.

### 1) Go to the repo root

```bash
cd /home/swu/bridge-vm-config-repo
```

### 2) Pull the latest live files into the mirror

```bash
./scripts/snapshot_from_live.sh
```

### 3) Verify the actual live bridge state before committing

```bash
./scripts/verify_live_state.sh
```

### 4) Create a timestamped commit snapshot

```bash
./scripts/prepare_commit_snapshot.sh
```

### 5) Review changes

```bash
git status
git diff --stat
git diff
```

### 6) Update docs and manifests if needed

Review and update these if architecture, runtime state, endpoints, services, manifests, or troubleshooting guidance changed:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `CURRENT_STAGE.md`
- `README.md`
- `MANIFEST/*.yaml`

Make sure the docs no longer describe the bridge issue as unresolved.

### 7) Review permissions and restart implications

Confirm that manifests reflect owner / group / mode changes and note whether these would require:

- `systemctl daemon-reload`
- service restart
- enable / disable / mask actions

### 8) Stage the changes

```bash
git add AGENTS.md PROJECT_STATUS.md CURRENT_STAGE.md MANIFEST/services_manifest.yaml \
  live-files/home/swu/bridge-docs/AGENTS.md \
  live-files/home/swu/bridge-docs/PROJECT_STATUS.md \
  live-files/home/swu/bridge-docs/CURRENT_STAGE.md \
  bridge_vm_pre_commit_procedure.md \
  PRE_COMMIT_PROCEDURE.md \
  .codex/skills/bridge-precommit-commit/SKILL.md
```

### 9) Commit with a precise message

Generic example:

```bash
git commit -m "docs: update bridge state after rosbridge runtime fix"
```

Current exact commit command reported by Codex for the present ready state:

```bash
cd /home/swu/bridge-vm-config-repo && git -c safe.directory=/home/swu/bridge-vm-config-repo commit -m "Update mirrored bridge docs and manifests for working post-fix state"
```

---

## Mandatory checks before commit

These must be true before committing:

- `ros1-dynamic-bridge.service` is active
- `rosbridge-websocket.service` is active
- `ros-map-export.service` is active
- port `9090` is listening on the intended managed rosbridge process
- `curl http://127.0.0.1:8081/map_meta.json` returns valid metadata
- manifests still match mirrored files and live paths
- backup / rollback folders that should not be committed are covered by `.gitignore`
- no manual shell process is shadowing a systemd-managed service
- docs match the current runtime state

---

## First-response troubleshooting rule

If the robot disappears from the map again, do **not** start by rewriting services or frontend code.

Check these first:

```bash
ps -ef | grep dynamic_bridge
sudo ss -ltnp | grep 9090
```

Then also check:

```bash
systemctl status ros1-dynamic-bridge.service --no-pager -l
systemctl status rosbridge-websocket.service --no-pager -l
systemctl status ros-map-export.service --no-pager -l
```

Useful runtime checks:

```bash
env -i HOME=/home/swu USER=swu LOGNAME=swu PATH=/usr/sbin:/usr/bin:/sbin:/bin sudo -u swu /bin/bash -lc "source /opt/ros/foxy/setup.bash; ros2 topic info /robot/robotnik_base_control/odom"
curl http://127.0.0.1:8081/map_meta.json
journalctl -u rosbridge-websocket.service -f
```

If remote UI transport is suspected, validate websocket publish delivery with an explicit typed subscribe to:

- `/robot/robotnik_base_control/odom`
- type: `nav_msgs/msg/Odometry`

---

## Recommended commit message patterns

Use commit messages that say what changed, why, and the operational effect.

Examples:

- `bridge: split dynamic_bridge and rosbridge into separate systemd services`
- `map-export: restore full-map metadata after cropped-map rollback`
- `docs: update bridge current state after remote websocket delivery fix`
- `bridge: mask legacy ros-bridge service and preserve split-service baseline`

---

## When not to commit yet

Do **not** commit yet if any of these are true:

- a manual shell process is still shadowing a systemd-managed service
- the repo mirror has not been refreshed from live files
- a service appears running, but verification commands still fail
- docs do not match the current runtime state
- manifests do not match the mirrored live files
- the working state has not been validated from both bridge-side and UI-side perspective

---

## Codex prompt

Paste this into Codex on the **bridge VM** when you want it to prepare the repo for a commit without making broad changes.

```text
Task: Refresh the bridge VM config repo from live state, verify the live bridge state, update all relevant mirrored docs/manifests/status files to match the current working post-fix reality, and report whether the repo is ready to commit. Do not dump full file contents unless explicitly asked.

Authoritative procedure:
- Repo root: /home/swu/bridge-vm-config-repo
- This repo mirrors scattered live files; live files remain in their OS locations
- Follow this sequence exactly:
  1. cd /home/swu/bridge-vm-config-repo
  2. ./scripts/snapshot_from_live.sh
  3. ./scripts/verify_live_state.sh
  4. ./scripts/prepare_commit_snapshot.sh
  5. review git status, git diff --stat, git diff
  6. update docs/manifests if runtime state changed
  7. stage relevant changes
- Do not commit yet unless I explicitly ask

Current facts that docs/manifests must reflect:
- Split-service architecture remains authoritative
- Legacy ros-bridge.service is masked/retired and must stay non-authoritative
- Root cause of the missing robot was stale/rogue runtime ownership around rosbridge on port 9090
- Fix: rogue processes removed, managed bridge services restarted
- Current validated state:
  - 9090 owned only by intended rosbridge process
  - 8081 owned by map exporter
  - /robot/robotnik_base_control/odom is live
  - typed websocket subscribe receives odom publish frames
  - robot is visible and moving in the UI
- AMCL was not required for the successful fix
- No rollback is needed
- First-response troubleshooting rule:
  check `ps -ef | grep dynamic_bridge`
  and `sudo ss -ltnp | grep 9090`
  before editing service files

Important tracked mirror scope includes:
- /etc/systemd/system/ros1-dynamic-bridge.service
- /etc/systemd/system/rosbridge-websocket.service
- /etc/systemd/system/ros-map-export.service
- /home/swu/map_exporter/app.py
- /home/swu/map_exporter/run.sh
- /home/swu/bridge-docs/AGENTS.md
- /home/swu/bridge-docs/PROJECT_STATUS.md
- /home/swu/bridge-docs/CURRENT_STAGE.md

Your job:
1. Run the documented pre-commit workflow in order.
2. Update all relevant mirrored docs/manifests/status files so they match the current post-fix reality.
3. Create any missing relevant note only if necessary to keep the repo consistent with the documented procedure.
4. Do not make broad runtime/service changes now unless verify_live_state reveals a real mismatch.
5. Stage the relevant updated files only.
6. Report only:
   - files changed
   - one-line summary per file
   - whether any expected file/script was missing
   - exact git status
   - exact git diff --stat
   - exact commit command to run next
   - final line: READY TO COMMIT or NOT READY

Do not print full file contents.
```

---

## Optional final manual commands

If Codex reports `READY TO COMMIT`, review once more manually:

```bash
cd /home/swu/bridge-vm-config-repo
git status
git diff --stat
```

Then commit manually with a precise message, for example:

```bash
git commit -m "docs: update bridge state after rosbridge runtime fix"
```

---

## Summary

This file contains the **updated / improved** manual execution guide and Codex operating prompt for the bridge VM repo workflow, not just a plain copy of the older included document. It incorporates the current post-fix bridge state, the split-service authoritative baseline, the first-response troubleshooting rule, and the current exact commit command reported by Codex for the ready-to-commit state.
