#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "No virtual environment found. Run scripts/setup/create_venv.sh first." >&2
    exit 1
fi

"$VENV_PYTHON" -m pip install -r "$PROJECT_DIR/requirements.txt"
echo "Requirements installed in .venv."
