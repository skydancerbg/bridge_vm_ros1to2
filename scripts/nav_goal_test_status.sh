#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="${NAV_GOAL_TEST_STATE_FILE:-/tmp/nav_goal_test/status.json}"

python3 - "$STATE_FILE" <<'PY'
import json
import os
import signal
import sys

state_file = sys.argv[1]
if not os.path.exists(state_file):
    print(json.dumps({"state": "idle", "running": False}, sort_keys=True))
    raise SystemExit(0)

with open(state_file, "r", encoding="ascii") as handle:
    data = json.load(handle)

pid = data.get("pid")
running = False
if isinstance(pid, int):
    try:
        os.kill(pid, 0)
        running = True
    except OSError:
        running = False

data["running"] = running
print(json.dumps(data, sort_keys=True))
PY
