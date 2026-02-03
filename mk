#!/usr/bin/env bash
# Thin wrapper - delegates to mk.py
set -euo pipefail
exec python3 "$(dirname "$0")/mk.py" "$@"
