# Key Files

## Live Runtime Files

Systemd:
- `/etc/systemd/system/ros-map-export.service`
- `/etc/systemd/system/ros1-dynamic-bridge.service`
- `/etc/systemd/system/rosbridge-websocket.service`
- `/etc/systemd/system/rosbridge-topic-advertiser.service`
- `/etc/systemd/system/ros-bridge.service`

Scripts:
- `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`
- `/usr/local/bin/bridge_startup.sh`
- `/home/swu/map_exporter/run.sh`
- `/home/swu/map_exporter/app.py`
- `/home/swu/bridge_support/ros2_topic_advertiser.py`

Generated files:
- `/home/swu/map_exporter/output/map.png`
- `/home/swu/map_exporter/output/map_meta.json`

## Documentation

Live/staged docs:
- `/home/swu/bridge-docs`
- `/home/swu/bridge-vm-config-repo/docs/Handoff_03-06-26_v1.md`
- `/home/swu/bridge-vm-config-repo/docs/bridge_current_state.md`
- `/home/swu/bridge-vm-config-repo/docs/bridge_full_project_documentation.md`
- `/home/swu/bridge-vm-config-repo/docs/post_fix_checkpoint_20260411.md`

This vault:
- `/home/swu/obsidian`

## Super Repo

Path:
- `/home/swu/bridge-vm-config-repo`

Important:
- `README.md`
- `CURRENT_STAGE.md`
- `PROJECT_STATUS.md`
- `MANIFEST/files_manifest.yaml`
- `MANIFEST/services_manifest.yaml`
- `scripts/snapshot_from_live.sh`
- `scripts/verify_live_state.sh`
- `scripts/restore_to_live.sh`

## Backup Folders

Historical only:
- `/home/swu/bridge-backups`
- `/home/swu/bridge-vm-config-repo/old-backups`

Use backups for comparison or rollback research, not as active source.

