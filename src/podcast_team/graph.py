from __future__ import annotations

from typing import Protocol

from podcast_team.agents.analyst import analyst_node
from podcast_team.agents.editor import editor_node
from podcast_team.agents.researcher import researcher_node
from podcast_team.logging_demo import DemoLogger
from podcast_team.settings import Settings
from podcast_team.state import PodcastState, make_initial_state


class GraphRunner(Protocol):
    def invoke(self, state: PodcastState) -> PodcastState:
        ...


class FallbackGraph:
    def __init__(self, *, settings: Settings, logger: DemoLogger) -> None:
        self.settings = settings
        self.logger = logger

    def invoke(self, state: PodcastState) -> PodcastState:
        self._merge(state, researcher_node(state, settings=self.settings, logger=self.logger))
        self._merge(state, analyst_node(state, settings=self.settings, logger=self.logger))
        self._merge(state, editor_node(state, settings=self.settings, logger=self.logger))
        return state

    @staticmethod
    def _merge(state: PodcastState, update: dict[str, object]) -> None:
        append_only_keys = {"structured_bullets", "warnings", "source_urls", "agent_trace"}
        for key, value in update.items():
            if key in append_only_keys:
                state[key].extend(value)  # type: ignore[index, union-attr]
            else:
                state[key] = value  # type: ignore[index]


def build_graph(*, settings: Settings, logger: DemoLogger) -> GraphRunner:
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return FallbackGraph(settings=settings, logger=logger)

    graph = StateGraph(PodcastState)
    graph.add_node("research", lambda state: researcher_node(state, settings=settings, logger=logger))
    graph.add_node("analyze", lambda state: analyst_node(state, settings=settings, logger=logger))
    graph.add_node("edit", lambda state: editor_node(state, settings=settings, logger=logger))
    graph.add_edge(START, "research")
    graph.add_edge("research", "analyze")
    graph.add_edge("analyze", "edit")
    graph.add_edge("edit", END)
    return graph.compile()


def run_team(
    *,
    topic: str,
    tone: str,
    settings: Settings | None = None,
    logger: DemoLogger | None = None,
) -> tuple[PodcastState, DemoLogger]:
    resolved_settings = settings or Settings.from_env()
    resolved_logger = logger or DemoLogger.create(resolved_settings.demo_runs_dir)
    graph = build_graph(settings=resolved_settings, logger=resolved_logger)
    final_state = graph.invoke(make_initial_state(topic=topic, tone=tone))
    resolved_logger.annotate()
    return final_state, resolved_logger
