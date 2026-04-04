from __future__ import annotations

import json

from podcast_team.llm import invoke_chat
from podcast_team.logging_demo import DemoLogger
from podcast_team.settings import Settings, temperature_for_model
from podcast_team.state import PodcastState, TraceEntry


def analyst_node(
    state: PodcastState,
    *,
    settings: Settings,
    logger: DemoLogger,
) -> dict[str, object]:
    logger.log_step_start("Analyst", "consuming researcher notes from shared state")

    if settings.use_mock_model:
        bullets = [
            f"Explain why {state['topic']} matters right now.",
            "Summarize the most credible patterns from the collected sources.",
            "Call out at least one uncertainty or open question.",
            "End with a practical takeaway for listeners or readers.",
        ]
        warnings = ["Mock mode warning: analysis is generated without a live model."]
    else:
        response = invoke_chat(
            system_prompt=(
                "You are an analyst who transforms research into a clear editorial outline. "
                "You have no tools and must rely only on the provided shared state. "
                "Return valid JSON with keys structured_bullets and warnings."
            ),
            user_prompt=(
                f"Topic: {state['topic']}\n"
                f"Tone: {state['tone']}\n\n"
                f"Research notes:\n{state['raw_research']}\n\n"
                "Create 4 to 6 structured bullets for the editor. "
                "Warnings should list factual caveats or places where certainty is low."
            ),
            model_name=settings.model_analyst,
            temperature=temperature_for_model(settings.model_analyst, 0.3),
        )
        parsed = _parse_analysis_json(response)
        bullets = parsed["structured_bullets"]
        warnings = parsed["warnings"]

    trace: TraceEntry = {
        "agent": "Analyst",
        "summary": f"Prepared {len(bullets)} bullets and {len(warnings)} warnings.",
        "tools_used": [],
    }
    logger.log_step_end("Analyst", f"generated {len(bullets)} structured bullets")
    return {
        "structured_bullets": bullets,
        "warnings": warnings,
        "agent_trace": [trace],
    }


def _parse_analysis_json(response: str) -> dict[str, list[str]]:
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return {
            "structured_bullets": [line.strip("- ").strip() for line in response.splitlines() if line.strip()],
            "warnings": ["Model response was not valid JSON; fallback parsing was used."],
        }

    bullets = [str(item).strip() for item in parsed.get("structured_bullets", []) if str(item).strip()]
    warnings = [str(item).strip() for item in parsed.get("warnings", []) if str(item).strip()]
    return {
        "structured_bullets": bullets,
        "warnings": warnings,
    }
