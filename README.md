# PMDS Social Agent

An early-stage project to help PMDS create social media posts. The proposed assistant would take a brief, links and images through Telegram, prepare an editable post using the existing Figma template, and provide a separate caption for human review.

The Python CLI uses LangChain and DeepSeek to draft a caption and hand a text-edit task to OpenCode. It targets one frame in a test copy of the PMDS template.

See [PROJECT_OUTLINE.md](docs/PROJECT_OUTLINE.md) for the proposed direction, [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the system design, and [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) for how the team will collaborate.

## Python environment

Install Python 3.11 or newer and use the setup guide to create or update the project’s virtual environment. [Local setup](docs/SETUP.md)

## Local credentials

Each developer uses their own DeepSeek API key. For local testing, enter it in a separate terminal for the drafting CLI. This keeps the key out of the workspace. [DeepSeek API keys](https://platform.deepseek.com/api_keys) · [Shell commands for credential setup](docs/SETUP.md#local-credentials)

`OPENCODE_PASSWORD` is a password you choose for your local OpenCode server. The launcher and the CLI need the same value. You can set it in both terminals or put one `OPENCODE_PASSWORD` entry in an ignored `.env` at the repo root. Git ignores that file, but agents with filesystem access can still read it. Shell variables take precedence over file values.

The default model and drafting prompt live in [agent.json](src/agent/config/agent.json). Set `DEEPSEEK_MODEL` to override the model. The CLI defaults to `http://127.0.0.1:4096` and accepts an `OPENCODE_URL` override.

## Draft a test post

**Use DeepSeek sparingly and always notify the team before a live run.** Run the offline suite for routine development and use your own key. Ask the team lead about access, billing, or planned usage. [DeepSeek usage](docs/DEEPSEEK.md)

1. From the repo root with the virtual environment active, run `python -m scripts.start_opencode` in one terminal and leave it running. The launcher uses `OPENCODE_PASSWORD` from the local settings. OpenCode uses its own configured model and Figma authorization. [OpenCode setup](scripts/opencode_probe/README.md#setup)
2. Make an editable copy of the PMDS template. In the copy, select the target frame and use **Copy link to selection**. The link should contain `node-id=`.
3. In a second terminal at the repo root, activate the virtual environment and set your DeepSeek key. Run the CLI with the link you copied and a short brief describing the desired post and text changes. [Credential setup](docs/SETUP.md#local-credentials)

```sh
python -m src.agent --figma-url "https://www.figma.com/design/FILE_KEY/PMDS-Test?node-id=12-34" "Announce that PMDS volunteer applications close Friday."
```

The command submits one design task and prints the caption, frame link and OpenCode's reported result. Inspect the edited layers in Figma and review the caption. If the edit is blocked or unconfirmed, the command exits with an error and keeps the caption when it has one. After a timeout, check the OpenCode session and the frame before rerunning because the task may still finish. The team lead confirmed this workflow in a live test on November 19, 2026.

## Run the offline tests

```sh
python -m unittest discover -s tests -v
```

The suite uses a fake chat model and simulated OpenCode HTTP responses. Live verification requires the local credentials, running server and test frame above.
