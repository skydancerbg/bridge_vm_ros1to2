---
name: bridge-precommit-commit
description: Use for tasks in /home/swu/bridge-vm-config-repo about refreshing mirrored live files, verifying bridge runtime, updating mirrored docs and manifests to the current bridge state, staging relevant files, and committing verified bridge repo changes.
---

# Bridge Pre-Commit Commit

Use this skill when working in `/home/swu/bridge-vm-config-repo` on bridge-side pre-commit prep or commit tasks.

## Workflow

1. Confirm repo root first:
   - `cd /home/swu/bridge-vm-config-repo`
   - `pwd`
   - `git -c safe.directory=/home/swu/bridge-vm-config-repo rev-parse --show-toplevel`

2. Inspect the compact repo instructions before changing docs:
   - `AGENTS.md`
   - `bridge_vm_pre_commit_procedure.md`
   - `PRE_COMMIT_PROCEDURE.md`
   - `scripts/snapshot_from_live.sh`
   - `scripts/verify_live_state.sh`
   - `scripts/prepare_commit_snapshot.sh`

3. Run the bridge pre-commit workflow in order:
   - `./scripts/snapshot_from_live.sh`
   - `./scripts/verify_live_state.sh`
   - `./scripts/prepare_commit_snapshot.sh`
   - `git -c safe.directory=/home/swu/bridge-vm-config-repo status --short`
   - `git -c safe.directory=/home/swu/bridge-vm-config-repo diff --stat`
   - `git -c safe.directory=/home/swu/bridge-vm-config-repo diff`

4. Update mirrored docs/manifests only if they no longer match the current validated bridge state.

5. Stage only the relevant files.

6. Commit only if explicitly asked and the repo is actually ready.

## Current Post-Fix Baseline

- Split-service architecture is authoritative:
  - `ros1-dynamic-bridge.service`
  - `rosbridge-websocket.service`
  - `ros-map-export.service`
- Legacy `ros-bridge.service` is retired, masked, and non-authoritative.
- Root cause of the missing robot issue was stale or rogue runtime ownership around rosbridge on port `9090`.
- Resolution:
  - rogue processes removed
  - managed bridge services restarted
- Validated working state:
  - `9090` owned only by intended rosbridge process
  - `8081` owned by map exporter
  - `/robot/robotnik_base_control/odom` is live
  - typed websocket subscribe receives odom publish frames
  - major watchdog-driven bridge collapses are fixed
  - measured odom continuity is down to about `0.30 s` max gap with zero gaps over `0.5 s` in the validated run
  - robot is visible and moving in the UI
- `AMCL` was not required for the successful fix.
- Bridge-side repeatable nav-goal capture and status-driven run helpers now exist under `scripts/`.
- Remote sim-control/testing helpers and SSH workflow must remain documented.
- No rollback is needed.
- First-response troubleshooting rule:
  - `ps -ef | grep dynamic_bridge`
  - `sudo ss -ltnp | grep 9090`

## Safety Rules

- Do not commit unless explicitly asked.
- Do not make broad runtime changes during pre-commit prep unless verification reveals a real mismatch.
- Do not rewrite `AGENTS.md` broadly; keep bridge-specific additions compact.
- Do not dump full file contents unless explicitly asked.

## Standard Commit Command

```bash
cd /home/swu/bridge-vm-config-repo && git -c safe.directory=/home/swu/bridge-vm-config-repo commit -m "Update mirrored bridge docs and manifests for working post-fix state"
```

## Reporting Format

1. files changed
2. one-line summary per file
3. exact git status
4. exact git diff --stat
5. exact commit command
6. `READY TO COMMIT` or `NOT READY`
7. if committed: `COMMITTED`
