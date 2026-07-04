# Super Repo Workflow

## Path

`/home/swu/bridge-vm-config-repo`

## Purpose

The super repo is a Git-ready mirror of important bridge VM files without moving live system files out of their OS locations.

It is used for:
- Version control.
- Restore/rebuild workflow.
- Documentation.
- Snapshotting current live state.
- Repeatable verification.

## Authority Rule

Live OS files are authoritative.

Edit live paths first:
- `/etc/systemd/system/*`
- `/usr/local/bin/*`
- `/home/swu/map_exporter/*`
- `/home/swu/bridge_support/*`

Then mirror into the repo.

## Main Scripts

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/snapshot_from_live.sh
./scripts/verify_live_state.sh
./scripts/restore_to_live.sh
./scripts/prepare_commit_snapshot.sh
```

## Manifests

Files manifest:
- `/home/swu/bridge-vm-config-repo/MANIFEST/files_manifest.yaml`

Services manifest:
- `/home/swu/bridge-vm-config-repo/MANIFEST/services_manifest.yaml`

## Recommended Change Flow

1. Inspect current live service and endpoint state.
2. Edit live file.
3. Run syntax checks.
4. Restart affected service.
5. Verify endpoints/topics.
6. Run `snapshot_from_live.sh`.
7. Review `git diff`.
8. Commit from the super repo when valid.

## Current Repo State Note

The vault was created after the handoff docs were staged in the repo. Check `git status` before committing.

