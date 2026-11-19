# DeepSeek usage

- **Use the API sparingly.** Run the offline test suite during development. Make live requests only for checks that need the real API, use a short brief, and inspect each result before retrying.
- **Always notify the team before using DeepSeek for this project.** Say what you’re testing and how many live runs you expect, especially before repeated or automated runs.
- **Create your own API key.** Each developer uses their own DeepSeek account and key. Enter it in the terminal running the drafting CLI and keep it out of Git and team messages. [Create a DeepSeek API key](https://platform.deepseek.com/api_keys) · [Local credential setup](SETUP.md#local-credentials)
- **Ask the team lead** about account setup, billing, API keys, or whether a planned test warrants live usage.

The CLI defaults to `deepseek-flash`. OpenCode uses its own separately configured model. [Agent settings](../src/agent/config/agent.json)
