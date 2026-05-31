#!/usr/bin/env bash
#
# Install the project's git hooks into .git/hooks/.
# Safe to re-run; will overwrite existing hooks of the same name.
#
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

SRC=scripts/hooks
DST=.git/hooks

mkdir -p "$DST"

for hook in "$SRC"/*; do
    name=$(basename "$hook")
    cp "$hook" "$DST/$name"
    chmod +x "$DST/$name"
    echo "installed: $DST/$name"
done

echo 'Done. Bypass any hook with: git <cmd> --no-verify'
