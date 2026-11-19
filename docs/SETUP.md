# Local setup

Each team member creates their own `.venv` on their computer. Install Python 3.11 or newer with `venv` support first. The commands below are run from the root of this repository.

## Python environment

### macOS and Linux

Create the environment and install the packages in `requirements.txt`:

```sh
./scripts/setup/create_venv.sh
```

Activate it in your current terminal:

```sh
source .venv/bin/activate
```

When `requirements.txt` changes, install the latest listed requirements into the existing environment:

```sh
./scripts/setup/update_venv.sh
```

### Windows Command Prompt

Create the environment and install the requirements:

```bat
scripts\setup\create_venv.bat
```

Activate it in your current terminal:

```bat
.venv\Scripts\activate.bat
```

When `requirements.txt` changes, update the existing environment:

```bat
scripts\setup\update_venv.bat
```

### Windows PowerShell

Create the environment and install the requirements:

```powershell
.\scripts\setup\create_venv.bat
```

Activate it in your current terminal:

```powershell
.\.venv\Scripts\Activate.ps1
```

When `requirements.txt` changes, update the existing environment:

```powershell
.\scripts\setup\update_venv.bat
```

The scripts use the environment's Python directly, so activation is not required to run the create or update commands. Activation makes `python` point to the environment in your current terminal. Run `deactivate` when you are done.

Use the update script if `.venv` already exists. It installs the requirements for the LangChain CLI. Installed packages that were removed from `requirements.txt` need to be uninstalled separately.

## Local credentials

Use your own DeepSeek key and notify the team before each live test. Keep API use to a minimum and ask the team lead about access or billing. [DeepSeek usage](DEEPSEEK.md)

Choose a password for your local OpenCode server. If you already have a value in `.env`, reuse it. To generate a new value, run this in your own terminal with the virtual environment active:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set `OPENCODE_PASSWORD` to that value in both the server and draft terminals, or add this line to your existing or new `.env` at the repo root:

```dotenv
OPENCODE_PASSWORD=<your-generated-password>
```

In a separate terminal for the drafting CLI, enter your own DeepSeek key using the command for your shell. The prompt hides the value as you type and sets it for that terminal session.

```zsh
# zsh
read -rs 'DEEPSEEK_API_KEY?DeepSeek API key: '
export DEEPSEEK_API_KEY
```

```bash
# Bash
read -rs -p 'DeepSeek API key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
```

```powershell
# PowerShell 7.1 or later
$env:DEEPSEEK_API_KEY = Read-Host 'DeepSeek API key' -MaskInput
```

Run the server and CLI after setting the credentials. [Draft a test post](../README.md#draft-a-test-post)

## Protect `.env` from coding agents

Git ignores `.env`. Access by a coding agent depends on the permissions of its active session. The project settings below cover the repo-root `.env` and nested files named `.env`. Create the settings files from the repo root. If either file already exists, merge the settings into it.

### Codex

Create `.codex/config.toml` with this profile:

```toml
default_permissions = "pmds-no-dotenv"
approval_policy = { granular = { sandbox_approval = false, request_permissions = false, rules = true, mcp_elicitations = true, skill_approval = true } }

[permissions.pmds-no-dotenv]
extends = ":workspace"

[permissions.pmds-no-dotenv.filesystem.":workspace_roots"]
".env" = "deny"
"**/.env" = "deny"
```

The profile allows normal workspace edits and denies access to the listed paths. It also disables requests to bypass or expand the sandbox. Codex loads project settings from trusted repos. In the desktop app, start a fresh local chat for this repo and select **Custom (config.toml)** or **pmds-no-dotenv** in the permissions menu. [Codex permission profiles](https://learn.chatgpt.com/docs/permissions) · [Desktop permissions menu](https://learn.chatgpt.com/docs/sandboxing)

### Claude Code

Create `.claude/settings.json` with these rules:

```json
{
  "permissions": {
    "deny": ["Read(/.env)", "Read(/**/.env)", "Edit(/.env)", "Edit(/**/.env)"]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyRead": ["./.env", "./**/.env"],
      "denyWrite": ["./.env", "./**/.env"]
    }
  }
}
```

The permission rules cover Claude’s file tools. The sandbox rules cover commands it runs. Start a fresh Claude Code session from the repo root on a platform with sandbox support. [Claude Code permissions](https://code.claude.com/docs/en/permissions) · [Claude Code sandbox](https://code.claude.com/docs/en/sandboxing)

Check the active settings with a disposable nested `.env` containing dummy values. Confirm that the agent gets a permission error when it tries to open that file through its shell, while it can still open an ordinary project file. In Claude Code, check the built-in **Read** tool with the dummy file too.
