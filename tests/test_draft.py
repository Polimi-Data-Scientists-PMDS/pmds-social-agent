import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError

from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

from scripts.start_opencode import main as start_opencode
from src.agent.__main__ import main

FRAME_URL = "https://www.figma.com/design/test-file/PMDS-Test?node-id=12-34"
BRIEF = "Announce that applications close Friday."
CAPTION = "Join PMDS! Volunteer applications close Friday."
DESIGN_INSTRUCTIONS = "Replace the headline with ‘Apply by Friday’."
ENVIRONMENT = {"DEEPSEEK_API_KEY": "test-key", "OPENCODE_PASSWORD": "test-password"}


class OpenCodeLauncherTests(unittest.TestCase):
    def test_passes_the_local_password_to_opencode(self):
        with TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "DEEPSEEK_API_KEY=offline-placeholder\nOPENCODE_PASSWORD=test-password\n",
                encoding="utf-8",
            )
            with (
                patch("src.agent.local_env.ENV_FILE", env_file),
                patch.dict(os.environ, {}, clear=True),
                patch("scripts.start_opencode.subprocess.call", return_value=0) as launch,
            ):
                self.assertEqual(start_opencode(), 0)
        self.assertEqual(
            launch.call_args.args[0],
            ["opencode", "serve", "--hostname", "127.0.0.1", "--port", "4096"],
        )
        self.assertEqual(launch.call_args.kwargs["env"], {"OPENCODE_PASSWORD": "test-password"})


class FakeToolCallingModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def tool_call(call_id):
    return {
        "name": "apply_figma_text",
        "args": {"caption": CAPTION, "design_instructions": DESIGN_INSTRUCTIONS},
        "id": call_id,
    }


def api_response(data):
    return io.BytesIO(json.dumps({"data": data}).encode())


def finished_messages(status="edited"):
    summary = "Headline updated." if status == "edited" else "No matching layer."
    reply = json.dumps({"status": status, "summary": summary})
    return [
        {"type": "idle", "outcome": "succeeded"},
        {"type": "assistant", "content": [{"type": "text", "text": reply}]},
    ]


class DraftCLITests(unittest.TestCase):
    def run_draft(
        self, responses, *, reply=None, environment=None, frame_url=FRAME_URL, dotenv=None
    ):
        if reply is None:
            reply = AIMessage(content="", tool_calls=[tool_call("first")])
        model = FakeToolCallingModel(messages=iter([reply]))
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            TemporaryDirectory() as directory,
            patch("src.agent.local_env.ENV_FILE", Path(directory) / ".env") as env_file,
            patch.dict(os.environ, ENVIRONMENT if environment is None else environment, clear=True),
            patch("src.agent.__main__.create_model", return_value=model) as create_model,
            patch("src.agent.opencode.urlopen", side_effect=responses) as http,
            patch("src.agent.opencode.time.sleep"),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            if dotenv is not None:
                env_file.write_text(dotenv, encoding="utf-8")
            try:
                status = main(["--figma-url", frame_url, BRIEF])
            except SystemExit as exc:
                status = exc.code
        return status, stdout.getvalue(), stderr.getvalue(), http, create_model

    def test_reads_local_credentials_with_shell_overrides(self):
        status, stdout, stderr, http, create_model = self.run_draft(
            [
                api_response({"id": "test-session"}),
                api_response({}),
                api_response(finished_messages()),
            ],
            dotenv=(
                "DEEPSEEK_API_KEY=offline-placeholder\n"
                "OPENCODE_PASSWORD=test-password\n"
                "DEEPSEEK_MODEL=deepseek-flash\n"
            ),
            environment={"DEEPSEEK_MODEL": "deepseek-v4-pro"},
        )
        create_model.assert_called_once_with("deepseek-v4-pro", "offline-placeholder")
        self.assertEqual(
            http.call_args_list[0].args[0].get_header("Authorization"),
            "Basic b3BlbmNvZGU6dGVzdC1wYXNzd29yZA==",
        )
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn(CAPTION, stdout)

    def test_sends_design_instructions_to_open_code_and_prints_caption(self):
        status, stdout, stderr, http, create_model = self.run_draft(
            [
                api_response({"id": "test-session"}),
                api_response({}),
                api_response([]),
                api_response(finished_messages()),
            ],
            environment=ENVIRONMENT | {"DEEPSEEK_MODEL": "deepseek-v4-pro"},
        )

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        create_model.assert_called_once_with("deepseek-v4-pro", "test-key")
        self.assertIn(CAPTION, stdout)
        self.assertIn(FRAME_URL, stdout)
        self.assertIn("reported the edit complete", stdout)
        requests = [call.args[0] for call in http.call_args_list]
        self.assertEqual(
            [request.get_method() for request in requests], ["POST", "POST", "GET", "GET"]
        )
        self.assertEqual(
            [request.selector for request in requests],
            [
                "/api/session",
                "/api/session/test-session/prompt",
                "/api/session/test-session/message?order=desc",
                "/api/session/test-session/message?order=desc",
            ],
        )
        self.assertEqual(requests[0].origin_req_host, "127.0.0.1")
        self.assertEqual(
            requests[0].get_header("Authorization"), "Basic b3BlbmNvZGU6dGVzdC1wYXNzd29yZA=="
        )
        prompt = json.loads(requests[1].data)["text"]
        self.assertIn(FRAME_URL, prompt)
        self.assertIn(DESIGN_INSTRUCTIONS, prompt)
        self.assertNotIn(CAPTION, prompt)

    def test_duplicate_tool_calls_submit_once(self):
        status, stdout, _, http, _ = self.run_draft(
            [
                api_response({"id": "test-session"}),
                api_response({}),
                api_response(finished_messages()),
            ],
            reply=AIMessage(content="", tool_calls=[tool_call("first"), tool_call("duplicate")]),
        )
        self.assertEqual(status, 0)
        self.assertIn(CAPTION, stdout)
        self.assertEqual(http.call_count, 3)

    def test_no_tool_call_makes_no_http_requests(self):
        status, _, stderr, http, _ = self.run_draft(
            [], reply=AIMessage(content="Please clarify the brief.")
        )
        self.assertEqual(status, 1)
        self.assertIn("did not supply a caption and design instructions", stderr)
        http.assert_not_called()

    def test_missing_configuration_stops_before_creating_a_model(self):
        for missing in ENVIRONMENT:
            with self.subTest(missing=missing):
                status, _, stderr, http, create_model = self.run_draft(
                    [],
                    environment={key: value for key, value in ENVIRONMENT.items() if key != missing},
                )
                self.assertEqual(status, 2)
                self.assertIn(missing, stderr)
                http.assert_not_called()
                create_model.assert_not_called()

    def test_file_or_default_page_link_is_rejected(self):
        file_url = FRAME_URL.split("?")[0]
        for frame_url in (file_url, f"{file_url}?node-id=0-1"):
            with self.subTest(frame_url=frame_url):
                status, _, stderr, http, create_model = self.run_draft([], frame_url=frame_url)
                self.assertEqual(status, 2)
                self.assertIn("Copy link to selection", stderr)
                http.assert_not_called()
                create_model.assert_not_called()

    def test_blocked_edit_keeps_caption(self):
        status, stdout, stderr, _, _ = self.run_draft(
            [
                api_response({"id": "test-session"}),
                api_response({}),
                api_response(finished_messages("blocked")),
            ]
        )
        self.assertEqual(status, 1)
        self.assertIn(CAPTION, stdout)
        self.assertIn("test-session", stdout)
        self.assertIn("OpenCode reported a blocker. No matching layer.", stderr)

    def test_invalid_reply_is_unconfirmed(self):
        response = io.BytesIO(b"not a JSON response")
        status, stdout, stderr, _, _ = self.run_draft(
            [api_response({"id": "test-session"}), api_response({}), response]
        )
        self.assertEqual(status, 1)
        self.assertIn(CAPTION, stdout)
        self.assertIn("Design edit unconfirmed", stderr)

    def test_session_success_without_edit_report_is_unconfirmed(self):
        messages = [{"type": "idle", "outcome": "succeeded"}]
        status, stdout, stderr, _, _ = self.run_draft(
            [api_response({"id": "test-session"}), api_response({}), api_response(messages)]
        )
        self.assertEqual(status, 1)
        self.assertIn(CAPTION, stdout)
        self.assertIn("Design edit unconfirmed", stderr)

    def test_timeout_keeps_caption_and_session_for_review(self):
        with patch("src.agent.opencode.POLL_TIMEOUT", 0):
            status, stdout, stderr, http, _ = self.run_draft(
                [api_response({"id": "test-session"}), api_response({})]
            )
        self.assertEqual(status, 1)
        self.assertIn(CAPTION, stdout)
        self.assertIn("test-session", stdout)
        self.assertIn("did not finish", stderr)
        self.assertIn("Inspect the OpenCode session and Figma frame before rerunning", stderr)
        self.assertEqual(http.call_count, 2)

    def test_opencode_authorization_error_keeps_caption(self):
        denied = HTTPError("http://127.0.0.1:4096/api/session", 401, "Unauthorized", {}, None)
        status, stdout, stderr, http, _ = self.run_draft([denied])
        self.assertEqual(status, 1)
        self.assertIn(CAPTION, stdout)
        self.assertIn("OPENCODE_PASSWORD", stderr)
        self.assertEqual(http.call_count, 1)
