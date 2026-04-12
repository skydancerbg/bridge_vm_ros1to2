# Bridge VM Config Repo

This repository is a Git-ready mirror of the important bridge VM files without moving the live system files out of their OS locations.

It is intended to be used as:
- a version-controlled mirror of the live bridge configuration
- a restore and rebuild toolkit
- a documentation and handoff bundle
- a commit-time snapshot workspace

Live files remain authoritative in their real locations, including:
- `/etc/systemd/system/`
- `/usr/local/bin/`
- `/home/swu/map_exporter/`
- `/home/swu/bridge-docs/`
- `/home/swu/bridge_support/`

The mirrored copies live under `live-files/`. Use the scripts in `scripts/` to refresh the mirror from live state, verify the live VM, create commit snapshots, and restore mirrored files back to the live system when needed.

For bridge-driven testing, passwordless SSH from this VM to the sim VM at `10.25.25.115` is confirmed. Use the helper scripts in `scripts/` for remote sim status checks and the standard restart entrypoint `/home/swu/restart_neo_workshop_navigation.sh`; they invoke SSH through local user `swu` so they work from the usual bridge-side Codex session.

This repo also carries the bridge-side navigation test helpers used in the current stage:
- captured RViz 2D Nav Goal listener
- status-driven 4-goal repeatable runner
- cancel and status helpers for SSH-driven UI VM testing
