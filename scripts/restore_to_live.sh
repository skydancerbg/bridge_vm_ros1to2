#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "$ROOT" <<'PY'
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
files = json.loads((root / "MANIFEST" / "files_manifest.yaml").read_text())
permissions = {
    item["live_path"]: item
    for item in json.loads((root / "MANIFEST" / "permissions_manifest.yaml").read_text())
}
services = json.loads((root / "MANIFEST" / "services_manifest.yaml").read_text())

daemon_reload_needed = False

for item in files:
    repo_path = root / item["repo_path"]
    live_path = pathlib.Path(item["live_path"])
    if not repo_path.exists():
        print(f"skip missing repo file: {repo_path}")
        continue
    meta = permissions.get(item["live_path"])
    mode = meta["mode"] if meta else "644"
    owner = meta["owner"] if meta else "root"
    group = meta["group"] if meta else "root"
    subprocess.run(
        ["sudo", "install", "-D", "-m", mode, str(repo_path), str(live_path)],
        check=True,
    )
    subprocess.run(
        ["sudo", "chown", f"{owner}:{group}", str(live_path)],
        check=True,
    )
    print(f"restored {live_path}")
    if str(live_path).startswith("/etc/systemd/system/"):
        daemon_reload_needed = True

doc_map = {
    root / "AGENTS.md": pathlib.Path("/home/swu/bridge-docs/AGENTS.md"),
    root / "PROJECT_STATUS.md": pathlib.Path("/home/swu/bridge-docs/PROJECT_STATUS.md"),
    root / "CURRENT_STAGE.md": pathlib.Path("/home/swu/bridge-docs/CURRENT_STAGE.md"),
}

for repo_file, live_file in doc_map.items():
    if repo_file.exists():
        subprocess.run(["sudo", "install", "-D", "-m", "644", str(repo_file), str(live_file)], check=True)
        print(f"restored {live_file}")

if daemon_reload_needed:
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    print("ran: sudo systemctl daemon-reload")

print("review and run only the needed restart commands:")
for service in services:
    for cmd in service.get("restart_commands", []):
        print(f"- {cmd}")
PY
