#!/usr/bin/env python3
"""Send one text request to an already-running OpenCode 2 server."""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request


def request(base_url, path, password, payload=None):
    auth = base64.b64encode(f"opencode:{password}".encode()).decode()
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        base_url + path,
        data=body,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)["data"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="Text to send to OpenCode")
    parser.add_argument("--url", default="http://127.0.0.1:4096")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    password = os.environ.get("OPENCODE_PASSWORD")
    if not password:
        parser.error("set OPENCODE_PASSWORD to the password of the running server")
    try:
        session = request(args.url, "/api/session", password, {"title": "PMDS API probe"})
        session_id = session["id"]
        request(args.url, f"/api/session/{session_id}/prompt", password, {"text": args.prompt})
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            messages = request(args.url, f"/api/session/{session_id}/message", password)
            if messages and messages[0].get("type") == "idle":
                if messages[0].get("outcome") != "succeeded":
                    raise RuntimeError(f"OpenCode finished with: {messages[0].get('outcome')}")
                answer = next((m for m in messages if m.get("type") == "assistant"), None)
                if not answer:
                    raise RuntimeError("OpenCode finished without an assistant response")
                print("\n".join(p.get("text", "") for p in answer.get("content", []) if p.get("type") == "text"))
                return
            time.sleep(1)
        raise TimeoutError(f"No completed response within {args.timeout} seconds; session: {session_id}")
    except (urllib.error.URLError, RuntimeError, TimeoutError, KeyError) as exc:
        print(f"OpenCode probe failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
