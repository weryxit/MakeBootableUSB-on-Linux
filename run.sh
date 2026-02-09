#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Re-run the script with sudo if it wasn't started as root.
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  exec sudo -- "$0" "$@"
fi

PYTHON_BIN="python3"
if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
fi

exec "$PYTHON_BIN" -m mbulinux "$@"
