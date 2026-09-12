#!/usr/bin/env sh
# subaru-skills harness entry point.
# Runs every check, aggregates results, and exits non-zero when a NEW blocking finding appears.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 2
PY="$PYTHON"
if [ -z "$PY" ]; then
  PY=python3
fi
BASELINE="tools/baseline.json"
CHECKS="validate_skills check_links check_consistency check_assets check_style_system check_installability"
status=0

echo "== subaru-skills harness =="
for c in $CHECKS; do
  printf '\n-- %s --\n' "$c"
  "$PY" "tools/$c.py" --baseline "$BASELINE" || status=1
done

printf '\n'
if [ "$status" -eq 0 ]; then
  echo "harness: PASS (new warnings above, if any, are non-blocking)"
else
  echo "harness: FAIL (new blocking findings; fix them or record deliberate debt with 'make baseline')"
fi
exit "$status"
