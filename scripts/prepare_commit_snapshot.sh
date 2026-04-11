#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS="$(date +%Y%m%d_%H%M%S)"
SNAPSHOT_DIR="$ROOT/commit-snapshots/snapshot_$TS"

mkdir -p "$SNAPSHOT_DIR"
cp -a "$ROOT/MANIFEST" "$SNAPSHOT_DIR/"
cp -a "$ROOT/live-files" "$SNAPSHOT_DIR/"
cp -a "$ROOT/docs" "$SNAPSHOT_DIR/"
cp -a "$ROOT/scripts" "$SNAPSHOT_DIR/"
cp -a "$ROOT/README.md" "$ROOT/AGENTS.md" "$ROOT/PROJECT_STATUS.md" "$ROOT/CURRENT_STAGE.md" "$ROOT/PRE_COMMIT_PROCEDURE.md" "$ROOT/.gitignore" "$SNAPSHOT_DIR/"

cat > "$SNAPSHOT_DIR/snapshot_manifest.json" <<EOF
{
  "timestamp": "$TS",
  "source_repo_root": "$ROOT",
  "snapshot_dir": "$SNAPSHOT_DIR"
}
EOF

echo "$SNAPSHOT_DIR"
