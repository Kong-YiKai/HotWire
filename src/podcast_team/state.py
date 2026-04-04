from __future__ import annotations

import operator
from typing import Annotated, TypedDict


class TraceEntry(TypedDict):
    agent: str
    summary: str
    tools_used: list[str]


class PodcastState(TypedDict):
    topic: str
    tone: str
    raw_research: str
    structured_bullets: Annotated[list[str], operator.add]
    warnings: Annotated[list[str], operator.add]
    source_urls: Annotated[list[str], operator.add]
    final_markdown: str
    agent_trace: Annotated[list[TraceEntry], operator.add]


def make_initial_state(topic: str, tone: str) -> PodcastState:
    return {
        "topic": topic,
        "tone": tone,
        "raw_research": "",
        "structured_bullets": [],
        "warnings": [],
        "source_urls": [],
        "final_markdown": "",
        "agent_trace": [],
    }
