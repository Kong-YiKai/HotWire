from __future__ import annotations

import json

from podcast_team.llm import invoke_chat
from podcast_team.logging_demo import DemoLogger
from podcast_team.settings import Settings, temperature_for_model
from podcast_team.state import PodcastState, TraceEntry
from podcast_team.tools import format_search_results, search_web


def researcher_node(
    state: PodcastState,
    *,
    settings: Settings,
    logger: DemoLogger,
) -> dict[str, object]:
    logger.log_step_start("Researcher", f"topic={state['topic']} tone={state['tone']}")
    results = search_web(
        query=state["topic"],
        max_results=settings.search_max_results,
        use_mock=settings.use_mock_model,
    )
    urls = [result["url"] for result in results]
    logger.log_tool_call(
        "Researcher",
        "web_search",
        json.dumps({"query": state["topic"], "max_results": settings.search_max_results}),
        f"returned {len(results)} results",
    )

    if settings.use_mock_model:
        raw_research = _mock_research(state["topic"], results)
    else:
        raw_research = invoke_chat(
            system_prompt=(
                "You are a web research specialist. Summarize fresh, factual notes for the topic. "
                "Use only the supplied search results. Include a short source-based synthesis and note "
                "uncertainty when the evidence is thin."
            ),
            user_prompt=(
                f"Topic: {state['topic']}\n"
                f"Desired tone for final output: {state['tone']}\n\n"
                f"Search results:\n{format_search_results(results)}\n\n"
                "Return concise prose notes followed by a short list of the most useful source URLs."
            ),
            model_name=settings.model_researcher,
            temperature=temperature_for_model(settings.model_researcher, 0.2),
        )

    trace: TraceEntry = {
        "agent": "Researcher",
        "summary": f"Collected {len(results)} sources and produced research notes.",
        "tools_used": ["web_search"],
    }
    logger.log_step_end("Researcher", "research notes stored in shared state")
    return {
        "raw_research": raw_research,
        "source_urls": urls,
        "agent_trace": [trace],
    }


def _mock_research(topic: str, results: list[dict[str, str]]) -> str:
    lines = [f"Research brief for {topic}:"]
    for result in results:
        lines.append(f"- {result['title']}: {result['snippet']} ({result['url']})")
    lines.append("- Confidence note: this is mock mode, so the sources above are synthetic.")
    return "\n".join(lines)
