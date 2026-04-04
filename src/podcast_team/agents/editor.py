from __future__ import annotations

import json

from podcast_team.llm import invoke_chat
from podcast_team.logging_demo import DemoLogger
from podcast_team.settings import Settings, temperature_for_model
from podcast_team.state import PodcastState, TraceEntry
from podcast_team.tools import word_count


def editor_node(
    state: PodcastState,
    *,
    settings: Settings,
    logger: DemoLogger,
) -> dict[str, object]:
    logger.log_step_start("ChiefEditor", "turning bullets into final markdown")

    if settings.use_mock_model:
        final_markdown = _mock_markdown(state)
    else:
        final_markdown = invoke_chat(
            system_prompt=(
                "You are the chief editor. Turn the provided bullets into polished Markdown for a "
                "topic article or short podcast script. You do not have web access. Preserve nuance "
                "from any warnings while matching the requested tone."
            ),
            user_prompt=(
                f"Topic: {state['topic']}\n"
                f"Tone: {state['tone']}\n\n"
                f"Bullets:\n- " + "\n- ".join(state["structured_bullets"]) + "\n\n"
                f"Warnings:\n- " + ("\n- ".join(state["warnings"]) if state["warnings"] else "None") + "\n\n"
                "Return Markdown with a title, short introduction, 3 to 4 sections, and a closing takeaway."
            ),
            model_name=settings.model_editor,
            temperature=temperature_for_model(settings.model_editor, 0.7),
        )

    count = word_count(final_markdown)
    logger.log_tool_call(
        "ChiefEditor",
        "word_count",
        json.dumps({"text_preview": final_markdown[:80]}),
        f"word count={count}",
    )

    trace: TraceEntry = {
        "agent": "ChiefEditor",
        "summary": f"Produced final markdown draft with {count} words.",
        "tools_used": ["word_count"],
    }
    logger.log_step_end("ChiefEditor", "final markdown stored in shared state")
    return {
        "final_markdown": final_markdown,
        "agent_trace": [trace],
    }


def _mock_markdown(state: PodcastState) -> str:
    bullet_lines = "\n".join(f"- {item}" for item in state["structured_bullets"])
    warning_line = "\n".join(f"- {item}" for item in state["warnings"]) or "- No warnings."
    return f"""# {state['topic']}

## Opening
This mock-mode draft uses a {state['tone']} tone and demonstrates the editor handoff.

## Key Points
{bullet_lines}

## Caveats
{warning_line}

## Closing Takeaway
The workflow is ready for a live model once environment variables and dependencies are installed.
"""
