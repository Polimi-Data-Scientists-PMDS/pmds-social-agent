# PMDS Social Agent

An early-stage project to help PMDS create social media posts. The proposed assistant would take a brief, links and images through Telegram, prepare an editable post using the existing Figma template, and provide a separate caption for human review.

The Python CLI uses LangChain and DeepSeek to draft a caption and hand a text-edit task to OpenCode. It targets one frame in a test copy of the PMDS template.

See [PROJECT_OUTLINE.md](docs/PROJECT_OUTLINE.md) for the proposed direction, [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the system design, and [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) for how the team will collaborate.

## Python environment

Install Python 3.11 or newer with virtual-environment support. From the project root, create a local `.venv` and install the dependencies in `requirements.txt`:

```sh
# macOS / Linux
./scripts/setup/create_venv.sh
source .venv/bin/activate
```

```bat
REM Windows Command Prompt
scripts\setup\create_venv.bat
.venv\Scripts\activate.bat
```

In Windows PowerShell, run `./scripts/setup/create_venv.bat` and activate with `./.venv/Scripts/Activate.ps1`. Each team member creates their own environment. When `requirements.txt` changes or `.venv` already exists, run `./scripts/setup/update_venv.sh` on macOS/Linux or `scripts\setup\update_venv.bat` on Windows.

## Draft a test post

1. Create a DeepSeek API key and set `DEEPSEEK_API_KEY` in the terminal where you will run the CLI. The default model and drafting prompt live in [agent.json](src/agent/config/agent.json). Set `DEEPSEEK_MODEL` to override the default model. [DeepSeek API keys](https://platform.deepseek.com/api_keys)
2. In another terminal, run `opencode serve --hostname 127.0.0.1 --port 4096` from the repo root, where [opencode.json](opencode.json) configures Figma MCP. Set the same `OPENCODE_PASSWORD` in both terminals. The CLI defaults to `http://127.0.0.1:4096` and accepts an `OPENCODE_URL` override. OpenCode uses its own configured model and Figma authorization. [OpenCode setup](scripts/opencode_probe/README.md#setup)
3. Make an editable copy of the PMDS template. In the copy, select the target frame and use **Copy link to selection**. The link should contain `node-id=`. Keep credentials in your local environment and out of the repository.
4. Run from the project root with the virtual environment active. Replace the example frame link with the one you copied.

```sh
python -m src.agent --figma-url "https://www.figma.com/design/FILE_KEY/PMDS-Test?node-id=12-34" "Announce that PMDS volunteer applications close Friday."
```

The command submits one design task and prints the caption, frame link and OpenCode's reported result. Inspect the edited layers in Figma and review the caption. If the edit is blocked or unconfirmed, the command exits with an error and keeps the caption when it has one. After a timeout, check the OpenCode session and the frame before rerunning because the task may still finish.

## Run the offline tests

```sh
python -m unittest discover -s tests -v
```

The suite uses a fake chat model and simulated OpenCode HTTP responses. Live verification requires the local credentials, running server and test frame above.
