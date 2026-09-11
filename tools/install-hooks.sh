#!/usr/bin/env sh
# Install a git pre-commit hook that runs the repo harness.
# Refuses to overwrite a foreign hook unless --force is given.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/.git/hooks/pre-commit"
FORCE=0
if [ "$1" = "--force" ]; then
  FORCE=1
fi
if [ ! -d "$ROOT/.git" ]; then
  echo "not a git repository (or .git is not a directory): $ROOT" >&2
  exit 2
fi
mkdir -p "$ROOT/.git/hooks"
if [ -f "$HOOK" ] && ! grep -q "subaru-skills harness" "$HOOK" && [ "$FORCE" -ne 1 ]; then
  echo "existing foreign pre-commit hook found; rerun with --force to replace" >&2
  exit 3
fi
cat > "$HOOK" <<'HOOKEOF'
#!/usr/bin/env sh
# subaru-skills harness pre-commit hook
if [ "$SKIP_HARNESS" = "1" ]; then
  echo "pre-commit: SKIP_HARNESS=1, skipping harness"
  exit 0
fi
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 2
echo "pre-commit: running make check"
make check
HOOKEOF
chmod +x "$HOOK"
echo "installed: $HOOK"
