# Python environment setup

Each team member creates their own `.venv` on their computer. Install Python 3 with `venv` support first. The commands below are run from the root of this repository.

## macOS and Linux

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

## Windows: Command Prompt

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

## Windows: PowerShell

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

The create script stops if `.venv` already exists; use the update script instead. The update script installs the listed requirements, but does not remove packages that have been removed from `requirements.txt`. Currently, the file contains no third-party packages because the existing probes use Python's standard library.
