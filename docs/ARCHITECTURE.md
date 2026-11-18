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

The CLI, agent and HTTP client run in one Python process. OpenCode is a separate running service. DeepSeek API credentials and the OpenCode HTTP password are configured in the local environment. OpenCode manages its own model credentials and Figma authorization.

## Verification

The CLI tests use a fake chat model with LangChain's actual tool dispatch and simulated OpenCode API responses. They cover the normal handoff, duplicate calls, invalid input or configuration, malformed responses, OpenCode authorization errors, blocked edits and timeouts.

An offline round trip through the DeepSeek adapter confirmed that it sends the tool schema and parses a tool call. An isolated OpenCode 2.3.0 server accepted Basic authentication and returned the expected session, prompt and message responses with model execution paused.

The earlier probes sent a real request to OpenCode, and the project lead reported seeing a test label in Figma after the initial sign-in. A live CLI run against a copy of the PMDS template is pending. Its acceptance check is a usable caption and updated text in the selected frame with the other layers and layout intact. [OpenCode probes](../scripts/opencode_probe/)

## Next milestones

Telegram input, images, revisions and cloud deployment are future work. Authentication after server restarts and long-running operation also need live verification. Hosting, credential lifecycle and possible cross-cloud failover remain open decisions.
