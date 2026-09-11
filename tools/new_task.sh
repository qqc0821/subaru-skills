#!/usr/bin/env sh
# Scaffold task artifacts from docs/templates/. Refuses to overwrite unless --force.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FORCE=0
if [ "$1" = "--force" ]; then
  FORCE=1
fi
for name in task_plan findings progress; do
  src="$ROOT/docs/templates/$name.md"
  dst="$ROOT/$name.md"
  if [ ! -f "$src" ]; then
    echo "missing template: $src" >&2
    exit 2
  fi
  if [ -e "$dst" ] && [ "$FORCE" -ne 1 ]; then
    echo "skip (exists): $dst   (use --force to overwrite)"
    continue
  fi
  cp "$src" "$dst"
  echo "created: $dst"
done
