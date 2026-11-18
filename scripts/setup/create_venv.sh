#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
VENV_DIR="$PROJECT_DIR/.venv"

if [ -e "$VENV_DIR" ]; then
    echo "A .venv already exists at $VENV_DIR. Run update_venv.sh to install requirements."
    exit 1
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install -r "$PROJECT_DIR/requirements.txt"
echo "Environment ready. Activate it with: source .venv/bin/activate (from the project root)"
