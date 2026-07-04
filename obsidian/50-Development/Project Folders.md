# Project Folders

## Live Project Folders

| Path | Purpose |
| --- | --- |
| `/home/swu/map_exporter` | Live HTTP map exporter app and output files. |
| `/home/swu/bridge_support` | Live helper scripts such as ROS 2 topic advertiser. |
| `/home/swu/bridge-docs` | Live operator docs and intended handoff destination. Root-owned in latest session. |
| `/home/swu/bridge-vm-config-repo` | Git-ready super repo/mirror/toolkit. |
| `/home/swu/bridge-backups` | Historical backups and rollback material. |
| `/usr/local/bin` | Live executable bridge/watchdog scripts. |
| `/etc/systemd/system` | Live systemd unit files. |

## Super Repo Folders

| Path | Purpose |
| --- | --- |
| `/home/swu/bridge-vm-config-repo/live-files` | Mirror of selected live files. |
| `/home/swu/bridge-vm-config-repo/MANIFEST` | File and service manifests. |
| `/home/swu/bridge-vm-config-repo/scripts` | Snapshot, restore, verify, remote sim, and nav-test scripts. |
| `/home/swu/bridge-vm-config-repo/docs` | Handoff and historical project docs. |
| `/home/swu/bridge-vm-config-repo/old-backups` | Archived rollback snapshots. |

## This Vault

Path:
- `/home/swu/obsidian`

Purpose:
- Human and AI-friendly project knowledge base.
- Does not replace live configs or super repo mirror.
- Should be updated after major service, architecture, or access changes.

## Paths To Avoid

Do not use these as primary development sources:
- `/home/swu/bridge-backups/*`
- `/home/swu/bridge-vm-config-repo/old-backups/*`
- `/home/swu/bridge-vm-config-repo/live-files/*`
- `/home/swu/.cache/*`
- `/home/swu/.config/*`
- `/home/swu/.ros/log/*`

Do not revive without explicit rollback decision:
- `/etc/systemd/system/ros-bridge.service`
- `/usr/local/bin/bridge_startup.sh`

