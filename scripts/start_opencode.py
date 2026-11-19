"""Start the local OpenCode server with the project's password."""

import os
import subprocess
import sys

from src.agent.local_env import PROJECT_ROOT, read_local_settings


def main() -> int:
    try:
        password = read_local_settings().get("OPENCODE_PASSWORD") or ""
    except (OSError, UnicodeError):
        print("Could not read the project .env file.", file=sys.stderr)
        return 1
    if not password.strip():
        print("Set OPENCODE_PASSWORD in .env or your environment.", file=sys.stderr)
        return 1

    try:
        return subprocess.call(
            ["opencode", "serve", "--hostname", "127.0.0.1", "--port", "4096"],
            cwd=PROJECT_ROOT,
            env={**os.environ, "OPENCODE_PASSWORD": password},
        )
    except FileNotFoundError:
        print("Install OpenCode 2 and make sure opencode is on your PATH.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
