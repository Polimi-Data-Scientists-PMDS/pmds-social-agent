"""Load project settings from the local file and the process environment."""

import os
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


def read_local_settings() -> dict[str, str | None]:
    return {**dotenv_values(ENV_FILE, interpolate=False), **os.environ}
