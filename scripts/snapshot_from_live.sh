#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "$ROOT" <<'PY'
import json
import os
import pathlib
import pwd
import grp
import shutil
import stat
import sys

root = pathlib.Path(sys.argv[1])
files_manifest = root / "MANIFEST" / "files_manifest.yaml"
perm_manifest = root / "MANIFEST" / "permissions_manifest.yaml"

files = json.loads(files_manifest.read_text())
permissions = []

for item in files:
    live = pathlib.Path(item["live_path"])
    repo = root / item["repo_path"]
    if not live.exists():
        print(f"skip missing: {live}")
        continue
    repo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(live, repo)
    st = live.stat()
    permissions.append(
        {
            "live_path": item["live_path"],
            "owner": pwd.getpwuid(st.st_uid).pw_name,
            "group": grp.getgrgid(st.st_gid).gr_name,
            "mode": format(stat.S_IMODE(st.st_mode), "o"),
        }
    )

doc_map = {
    pathlib.Path("/home/swu/bridge-docs/AGENTS.md"): root / "AGENTS.md",
    pathlib.Path("/home/swu/bridge-docs/PROJECT_STATUS.md"): root / "PROJECT_STATUS.md",
    pathlib.Path("/home/swu/bridge-docs/CURRENT_STAGE.md"): root / "CURRENT_STAGE.md",
}

for live, repo in doc_map.items():
    if live.exists():
        shutil.copy2(live, repo)

perm_manifest.write_text(json.dumps(permissions, indent=2) + "\n")
print(f"mirrored {len(permissions)} live files")
PY
