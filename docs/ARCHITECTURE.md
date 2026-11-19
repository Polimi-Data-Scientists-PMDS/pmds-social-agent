# Architecture

The first milestone is a local CLI that drafts one PMDS post from a brief and a frame link in a disposable template copy.

## CLI flow

```text
Brief + test frame URL → Python CLI
                           ↓ brief
                    LangChain + DeepSeek
                           ↓ tool call (caption, design instructions)
                      apply_figma_text ← test frame URL from Python
                           ↓ HTTP (frame URL, design instructions)
                    OpenCode + its own model
                           ↓ Figma MCP
                    Editable PMDS test frame
```

1. **CLI** validates the brief, frame link and environment settings. It keeps the frame URL and passes the brief to the agent.
2. **LangChain** gives DeepSeek the description and argument types for `apply_figma_text`. DeepSeek returns a tool call containing the caption and exact on-design copy. LangChain reads those arguments and invokes the Python function.
3. **Python tool** supplies the frame URL to the OpenCode client and limits the run to one design submission. It keeps the caption in the result and returns directly to the CLI.
4. **OpenCode client** uses HTTP Basic authentication to create an OpenCode 2 session, submit a prompt, and poll for an idle result. OpenCode's independently configured model uses the existing Figma MCP connection to inspect the target frame and apply text replacements.
5. **Review** starts with the caption, frame URL, session ID when available, and OpenCode's report. The CLI requires an explicit edit report after the session finishes. The reviewer checks that the intended Figma layers actually changed and reviews the caption before publication.

The CLI, agent and HTTP client run in one Python process. Each developer can supply their own DeepSeek key in the CLI terminal. OpenCode runs in a separate process and manages its own model credentials and Figma authorization. The OpenCode launcher and the CLI use the same local HTTP password. They read it from the shell environment or from the project's ignored `.env`, with shell values taking precedence. [Credential setup](SETUP.md#local-credentials)

## Verification

The CLI tests use a fake chat model with LangChain's actual tool dispatch and simulated OpenCode API responses. They cover the normal handoff, duplicate calls, invalid input or configuration, malformed responses, OpenCode authorization errors, blocked edits and timeouts.

An offline round trip through the DeepSeek adapter confirmed that it sends the tool schema and parses a tool call. An isolated OpenCode 2.3.0 server accepted Basic authentication and returned the expected session, prompt and message responses with model execution paused.

The team lead reported a successful live CLI run against a selected frame in a Figma test copy on November 19, 2026. For future live runs, review the caption and check that the intended text layers changed in Figma. Always notify the team before using DeepSeek and keep live runs to a minimum. [Draft a test post](../README.md#draft-a-test-post) · [DeepSeek usage](DEEPSEEK.md)

## Next milestones

Telegram input, images, revisions and cloud deployment are future work. Authentication after server restarts and long-running operation also need live verification. Hosting, credential lifecycle and possible cross-cloud failover remain open decisions.
