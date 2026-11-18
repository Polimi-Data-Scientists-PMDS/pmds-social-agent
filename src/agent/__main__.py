"""Command-line entry point for one PMDS post draft."""

import argparse
import os
import re
import sys
from urllib.parse import parse_qs, urlsplit

from openai import APIConnectionError, APIStatusError

from .agent import create_model, draft_post, load_agent_config
from .opencode import DEFAULT_URL, OpenCodeClient


def _figma_frame_url(value: str) -> str:
    try:
        url = urlsplit(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("provide a valid Figma frame URL") from exc
    path = url.path.split("/")
    node_ids = parse_qs(url.query, keep_blank_values=True).get("node-id", [])
    if (
        url.scheme != "https"
        or url.netloc not in {"www.figma.com", "figma.com"}
        or len(path) < 3
        or path[1] not in {"design", "file"}
        or not path[2]
        or len(node_ids) != 1
        or not re.fullmatch(r"[0-9]+[-:][0-9]+", node_ids[0])
        or node_ids[0].replace(":", "-") in {"0-0", "0-1"}
    ):
        raise argparse.ArgumentTypeError("use Copy link to selection on the Figma test frame")
    return value


def _opencode_url(value: str) -> str:
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError as exc:
        raise argparse.ArgumentTypeError("OPENCODE_URL must be a valid HTTP or HTTPS URL") from exc
    if (
        url.scheme not in {"http", "https"}
        or not url.hostname
        or port == 0
        or url.username is not None
        or url.query
        or url.fragment
    ):
        raise argparse.ArgumentTypeError("OPENCODE_URL must be an HTTP or HTTPS server URL")
    return value.rstrip("/")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.agent", description=__doc__)
    parser.add_argument("brief", help="Short brief for the social post")
    parser.add_argument(
        "--figma-url", required=True, type=_figma_frame_url, help="Figma test frame link"
    )
    args = parser.parse_args(argv)
    brief = args.brief.strip()
    if not brief:
        parser.error("provide a nonempty brief")

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    password = os.getenv("OPENCODE_PASSWORD", "")
    if not api_key:
        parser.error("set DEEPSEEK_API_KEY to your DeepSeek API key")
    if not password.strip():
        parser.error("set OPENCODE_PASSWORD to the running server's password")
    try:
        server_url = _opencode_url(os.getenv("OPENCODE_URL", DEFAULT_URL).strip())
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    try:
        config = load_agent_config()
    except (OSError, ValueError) as exc:
        parser.error(f"could not load src/agent/config/agent.json: {exc}")
    model_name = os.getenv("DEEPSEEK_MODEL", "").strip() or config.default_model

    model = create_model(model_name, api_key)
    opencode = OpenCodeClient(server_url, password)
    try:
        result = draft_post(brief, args.figma_url, model, opencode, system_prompt=config.system_prompt)
    except APIConnectionError:
        print("Could not complete the request to DeepSeek. Check your connection.", file=sys.stderr)
        return 1
    except APIStatusError as exc:
        hint = {
            400: "Check DEEPSEEK_MODEL.",
            401: "Check DEEPSEEK_API_KEY.",
            402: "Check the balance in your DeepSeek API account.",
            403: "Check access to the DeepSeek API.",
            429: "Check the DeepSeek API rate limit.",
        }.get(exc.status_code, "")
        print(f"DeepSeek returned HTTP {exc.status_code}. {hint}".rstrip(), file=sys.stderr)
        return 1

    if result is None:
        print(
            "DeepSeek did not supply a caption and design instructions. Review the brief.",
            file=sys.stderr,
        )
        return 1

    print(f"Caption\n{result.caption}\n\nFigma frame\n{args.figma_url}")
    design = result.design
    if design.session_id:
        print(f"OpenCode session {design.session_id}")
    if design.status == "edited":
        print(f"OpenCode reported the edit complete. {design.summary}")
        return 0
    if design.status == "blocked":
        print(f"OpenCode reported a blocker. {design.summary}", file=sys.stderr)
    else:
        print(f"Design edit unconfirmed. {design.summary}", file=sys.stderr)
    if design.session_id:
        print("Inspect the OpenCode session and Figma frame before rerunning.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
