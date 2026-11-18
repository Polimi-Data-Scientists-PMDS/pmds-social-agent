# Architecture

This document describes the intended application and what the current experiments have demonstrated. The application and LangChain agent have not been implemented yet.

## Intended flow

```text
User → command line initially; Telegram later
                  ↓
         Python application / workflow
                  ↓
      LangChain agent ↔ DeepSeek API
                  ↓ calls a Python tool
         OpenCode service + its model
                  ↓
           Figma MCP → Figma
                  ↓
     Editable draft + caption for human review
```

1. **User interface:** A simple command-line interface will be the initial way to submit a brief. Telegram is intended later for text, images and conversation.
2. **Application and workflow:** Python code will pass the request to the agent, coordinate the result and eventually manage things such as revisions and errors. Exact responsibilities and data formats are still to be designed.
3. **LangChain agent:** The agent will use the **DeepSeek API** as its model provider. It will help prepare a caption and design instructions and can request the OpenCode tool. The exact DeepSeek model, credentials, cost controls and implementation remain to be chosen and configured.
4. **OpenCode tool and service:** A Python function will communicate with a running OpenCode service over its HTTP API. OpenCode uses its own configured model and Figma MCP tools to carry out design tasks. It is a separate agent and model connection from the LangChain agent; either model can be configured independently.
5. **Figma and review:** The goal is an editable design plus a separate caption. A person reviews the result before publication.

The Python-to-OpenCode HTTP code can live in the same application as the workflow; it does not require another intermediary service. OpenCode itself must be running and reachable. Credentials for DeepSeek, OpenCode and Figma need separate configuration and must not be committed.

## What exists today

The scripts in [`scripts/opencode_probe`](../scripts/opencode_probe/) are feasibility experiments. A Python probe successfully sent a request to OpenCode. The project lead also reported seeing a test label created in Figma through the probe, without further interaction after the initial sign-in.

This demonstrates a basic edit, not the complete post workflow. The PMDS template, images, revisions, authentication after restarts and cloud operation remain to be tested as the application is built. The LangChain agent, DeepSeek connection, Telegram interface and application workflow are planned, not implemented.

## Deployment direction

Develop locally first. Later, the Python application and OpenCode service could run on a cloud machine, with the model providers and Figma accessed over the network. Hosting, operation, credential lifecycle and possible cross-cloud failover remain open decisions.
