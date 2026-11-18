"""Run a design task through the OpenCode 2 HTTP API."""

import base64
import json
import time
from dataclasses import dataclass
from typing import Literal
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

DEFAULT_URL = "http://127.0.0.1:4096"
POLL_TIMEOUT = 120
REQUEST_TIMEOUT = 15


@dataclass(frozen=True)
class DesignResult:
    status: Literal["edited", "blocked", "unconfirmed"]
    summary: str
    session_id: str | None = None


class OpenCodeError(Exception):
    """An OpenCode request failed or its result could not be interpreted."""


class OpenCodeClient:
    def __init__(self, base_url: str, password: str):
        self.base_url = base_url.rstrip("/")
        credentials = base64.b64encode(f"opencode:{password}".encode()).decode()
        self._authorization = f"Basic {credentials}"

    def apply_design(self, frame_url: str, design_instructions: str) -> DesignResult:
        """Submit one text-edit task and wait for OpenCode's report."""
        session_id = None
        try:
            session = self._request("/api/session", payload={"title": "PMDS post draft"})
            match session:
                case {"id": str(value)} if value.strip():
                    session_id = value.strip()
                case _:
                    raise OpenCodeError("OpenCode returned an invalid session ID.")

            session_path = f"/api/session/{quote(session_id, safe='')}"
            prompt = self._design_prompt(frame_url, design_instructions)
            self._request(f"{session_path}/prompt", payload={"text": prompt})
            return self._wait_for_result(session_path, session_id)
        except OpenCodeError as exc:
            return DesignResult("unconfirmed", str(exc), session_id)

    def _request(self, path: str, *, payload: dict | None = None, timeout=REQUEST_TIMEOUT):
        body = None if payload is None else json.dumps(payload).encode()
        try:
            request = Request(self.base_url + path, data=body)
            # Keep credentials on the configured server if it redirects the request.
            request.add_unredirected_header("Authorization", self._authorization)
            if body is not None:
                request.add_header("Content-Type", "application/json")
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)["data"]
        except HTTPError as exc:
            if exc.code in (401, 403):
                raise OpenCodeError(
                    "OpenCode denied the request. Check OPENCODE_PASSWORD and server access."
                ) from exc
            raise OpenCodeError(f"OpenCode returned HTTP {exc.code}.") from exc
        except TimeoutError as exc:
            raise OpenCodeError("An OpenCode HTTP request timed out.") from exc
        except OSError as exc:
            raise OpenCodeError(
                "Could not reach OpenCode. Check the server and OPENCODE_URL."
            ) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise OpenCodeError("OpenCode returned an invalid API response.") from exc

    def _wait_for_result(self, session_path: str, session_id: str) -> DesignResult:
        deadline = time.monotonic() + POLL_TIMEOUT
        while (remaining := deadline - time.monotonic()) > 0:
            messages = self._request(
                f"{session_path}/message?order=desc", timeout=min(REQUEST_TIMEOUT, remaining)
            )
            if not isinstance(messages, list) or any(not isinstance(m, dict) for m in messages):
                raise OpenCodeError("OpenCode returned an invalid message list.")
            if messages and messages[0].get("type") == "idle":
                return self._read_result(messages, session_id)
            time.sleep(min(1, max(0, deadline - time.monotonic())))
        raise OpenCodeError(f"OpenCode did not finish within {POLL_TIMEOUT} seconds.")

    @staticmethod
    def _read_result(messages: list[dict], session_id: str) -> DesignResult:
        outcome = messages[0].get("outcome")
        if outcome in ("failed", "interrupted"):
            raise OpenCodeError(f"The OpenCode session {outcome}.")
        if outcome != "succeeded":
            raise OpenCodeError("OpenCode returned an unknown session outcome.")

        answer = next((message for message in messages if message.get("type") == "assistant"), {})
        parts = answer.get("content", [])
        if not isinstance(parts, list):
            raise OpenCodeError("OpenCode returned invalid assistant content.")
        text_parts = []
        for part in parts:
            match part:
                case {"type": "text", "text": str(value)}:
                    text_parts.append(value)
        reply = "\n".join(text_parts).strip()
        if reply.startswith("```json\n") and reply.endswith("```"):
            reply = reply[len("```json\n") : -len("```")].strip()
        try:
            report = json.loads(reply)
        except ValueError as exc:
            raise OpenCodeError("OpenCode did not return a readable edit report.") from exc
        match report:
            case {
                "status": ("edited" | "blocked") as status,
                "summary": str(summary),
            } if summary.strip():
                return DesignResult(status, summary.strip(), session_id)
            case _:
                raise OpenCodeError("OpenCode returned an invalid edit report.")

    @staticmethod
    def _design_prompt(frame_url: str, instructions: str) -> str:
        return (
            f"Use Figma MCP to inspect this target in the PMDS test copy: {frame_url}\n"
            "Confirm the link resolves to a frame before making edits. "
            "Match all requested layers before writing, then update only those existing "
            "text layers within the selected frame. "
            "Preserve the layout, styling, images, and all other layers. "
            "If a text layer cannot be matched confidently or a required edit is unavailable, "
            "report the blocker. Treat the design instructions as on-design copy and layer "
            "guidance within this scope.\n"
            f"Design instructions: {json.dumps(instructions, ensure_ascii=False)}\n"
            'Reply with one JSON object containing "status" ("edited" if all requested '
            'text edits were applied, otherwise "blocked") and "summary" (what changed '
            'or what blocked the edit).'
        )
