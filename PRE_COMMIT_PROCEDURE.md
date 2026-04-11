# Pre-Commit Procedure

Use this procedure before making a Git commit in this repo:

For Codex usage, prefer the repo-local skill:
- `Use the bridge-precommit-commit skill. Refresh the mirror from live state, verify the bridge runtime, update mirrored docs/manifests, stage the relevant files, and if everything is verified ready, commit with the standard post-fix message.`

1. Pull current live files into the repo mirror.
   - Run `./scripts/snapshot_from_live.sh`

2. Verify the live bridge state before snapshotting and committing.
   - Run `./scripts/verify_live_state.sh`

3. Create a timestamped commit snapshot of the current mirrored repo state.
   - Run `./scripts/prepare_commit_snapshot.sh`

4. Review the pending repo changes carefully.
   - Run `git status`
   - Run `git diff --stat`
   - Run `git diff`

5. Check whether file permissions, ownership, or service units changed.
   - Review `MANIFEST/permissions_manifest.yaml`
   - Review `MANIFEST/services_manifest.yaml`

6. Update project docs if the bridge architecture, active services, recovery steps, or current operating state changed.
   - Review `AGENTS.md`
   - Review `PROJECT_STATUS.md`
   - Review `CURRENT_STAGE.md`

7. Make a commit with a meaningful message that describes the actual bridge-side change.
   - Preferred current command: `cd /home/swu/bridge-vm-config-repo && git -c safe.directory=/home/swu/bridge-vm-config-repo commit -m "Update mirrored bridge docs and manifests for working post-fix state"`

8. If the commit captured changes that need to be restored later, note the relevant restore and restart procedure.
   - Use `./scripts/restore_to_live.sh`
   - Note whether `systemctl daemon-reload` and any service restarts are required
