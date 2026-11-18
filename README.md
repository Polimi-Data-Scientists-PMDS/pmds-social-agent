# PMDS Social Agent

An early-stage project to help PMDS create social media posts. The proposed assistant would take a brief, links and images through Telegram, prepare an editable post using the existing Figma template, and provide a separate caption for human review.

The intended stack is Python and LangChain. Initial scripts have tested a basic OpenCode-to-Figma edit; the application and full workflow have not been implemented yet.

See [PROJECT_OUTLINE.md](docs/PROJECT_OUTLINE.md) for the proposed direction, [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the system design, and [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) for how the team will collaborate.

## Python environment

Install Python 3 with virtual-environment support. From the project root, create a local `.venv` and install the dependencies in `requirements.txt`:

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

In Windows PowerShell, run `./scripts/setup/create_venv.bat` and activate with `./.venv/Scripts/Activate.ps1`. Each team member creates their own environment; it is not shared or committed. When `requirements.txt` changes, run `./scripts/setup/update_venv.sh` on macOS/Linux or `scripts\setup\update_venv.bat` on Windows. These scripts install listed requirements; they do not remove packages that were deleted from the list. The current probes use only the standard library, so the requirements file has no packages yet.
