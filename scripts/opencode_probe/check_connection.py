#!/usr/bin/env python3
"""Check an OpenCode 2 server and its Figma MCP connection, without editing files."""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request


def get(base_url, path, password):
    auth = base64.b64encode(f"opencode:{password}".encode()).decode()
    request = urllib.request.Request(base_url + path, headers={"Authorization": f"Basic {auth}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:4096")
    args = parser.parse_args()
    password = os.environ.get("OPENCODE_PASSWORD")
    if not password:
        parser.error("set OPENCODE_PASSWORD to the running server's password")
    try:
        info = get(args.url, "/api/info", password)
        print(f"OpenCode server reachable: version {info.get('version', 'unknown')}")
        result = get(args.url, "/api/mcp", password)
        servers = result.get("data", result)
        print("MCP connection status:")
        print(json.dumps(servers, indent=2))
        # Report the server's state; the operator must still verify its identity
        # and accessible Figma tools before relying on it.
    except (urllib.error.URLError, ValueError) as exc:
        print(f"Connection check failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
