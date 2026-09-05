#!/usr/bin/env bash
# Usage: hls_run.sh <workspace> <csim|csynth|cosim|impl|all> [config_file]
# Relative workspaces use DSE_PROJECT_ROOT or the caller's working directory.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
DSE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${DSE_PYTHON:-python3}" "$DSE_SCRIPT_DIR/hls_driver.py" "$@"
