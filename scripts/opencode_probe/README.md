# OpenCode and Figma feasibility probes

These small experiments investigate the intended route: Python → OpenCode server → model and Figma MCP. They use Python's standard library and OpenCode 2. They are experiments, not the production application or LangChain integration.

## Setup

Install OpenCode using its official instructions. Run the commands from the repo root, where `opencode.json` points OpenCode to Figma's remote MCP server. [OpenCode installation](https://opencode.ai/docs/) · [Project configuration](../../opencode.json)

```sh
opencode mcp list
opencode mcp auth figma
```

Figma authorization may open a browser and require you to sign in. Keep credentials out of Git. OpenCode may also need a configured model provider. Figma's remote write tools require a supported client and appropriate file permissions. [Figma setup](https://developers.figma.com/docs/figma-mcp-server/)

For the drafting CLI, use the project `.env` and the OpenCode launcher. The standalone probe commands below take `OPENCODE_PASSWORD` from the shell. [Local credentials](../../docs/SETUP.md#local-credentials)

Set your own password and start the service from the repo root.

```sh
export OPENCODE_PASSWORD='choose-a-local-test-password'
opencode serve --hostname 127.0.0.1 --port 4096
```

In another terminal at the repo root, set the same password.

```sh
export OPENCODE_PASSWORD='choose-a-local-test-password'
```

## Run the checks

1. `python3 scripts/opencode_probe/check_connection.py` checks the local server and prints its MCP statuses. A connection status is not proof that a Figma file can be edited.
2. `python3 scripts/opencode_probe/model_probe.py 'Say hello in one sentence.'` sends a real prompt through OpenCode to its configured model and prints its answer.
3. After Figma is connected, test a **file you are allowed to modify** with `model_probe.py`, giving it an explicit Figma file URL and a small reversible edit. Check the actual file yourself; an agent's success message alone is not proof. For example:

   ```sh
   python3 scripts/opencode_probe/model_probe.py 'In MY_TEST_FIGMA_FILE_URL, add a small text label saying PMDS TEST. Do not change other content. Return the resulting node or file link.'
   ```

Use a test file, not the production template. If OpenCode pauses for permissions or asks for interactive input, that is an experiment failure for unattended execution; do not assume a successful connection proves unattended operation. Check tool activity and inspect the actual design. Then repeat after restarting the service to investigate whether authorization persists. Cloud deployment and long-term token refresh are separate, still unverified checks.

The probes do not set tool permissions or bypass approval prompts. Stop the server with Control-C. Model availability, login and cost depend on the configured provider; Figma availability depends on account and file permissions. These probes create OpenCode sessions and do not automatically delete them.
