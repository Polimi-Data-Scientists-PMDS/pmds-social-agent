"""Turn a brief into a caption and a single Figma tool call."""

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.tools import tool
from langchain_core.language_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

from .opencode import DesignResult, OpenCodeClient


@dataclass(frozen=True)
class AgentConfig:
    default_model: str
    system_prompt: str


def load_agent_config() -> AgentConfig:
    path = Path(__file__).with_name("config") / "agent.json"
    match json.loads(path.read_text(encoding="utf-8")):
        case {
            "default_model": str(model),
            "system_prompt": str(prompt),
        } if model.strip() and prompt.strip():
            return AgentConfig(model.strip(), prompt.strip())
        case _:
            raise ValueError("default_model and system_prompt must be nonempty strings")


@dataclass(frozen=True)
class DraftResult:
    caption: str
    design: DesignResult


def create_model(model_name: str, api_key: str) -> ChatDeepSeek:
    return ChatDeepSeek(
        model=model_name,
        api_key=SecretStr(api_key),
        base_url="https://api.deepseek.com",
        extra_body={"thinking": {"type": "disabled"}},
        timeout=30,
        max_retries=0,
    )


def draft_post(
    brief: str,
    frame_url: str,
    model: BaseChatModel,
    opencode: OpenCodeClient,
    *,
    system_prompt: str,
) -> DraftResult | None:
    # Tool calls in the same model reply may run in parallel.
    submission_lock = Lock()
    submission_started = False
    draft_result: DraftResult | None = None

    @tool(return_direct=True)
    def apply_figma_text(caption: str, design_instructions: str) -> str:
        """Record the caption and submit exact replacement copy for the template text layers."""
        nonlocal submission_started, draft_result
        caption = caption.strip()
        design_instructions = design_instructions.strip()
        if not caption or not design_instructions:
            return "Both caption and design instructions are required."

        with submission_lock:
            if submission_started:
                return "This run already submitted its design task."
            submission_started = True

        design = opencode.apply_design(frame_url, design_instructions)
        draft_result = DraftResult(caption, design)
        return design.summary

    agent = create_agent(
        model,
        tools=[apply_figma_text],
        system_prompt=system_prompt,
        middleware=[ModelCallLimitMiddleware(run_limit=1)],
    )
    agent.invoke({"messages": [{"role": "user", "content": brief}]})
    return draft_result
