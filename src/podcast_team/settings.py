from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional for mock-only verification
    def load_dotenv() -> None:
        return None


@dataclass(slots=True)
class Settings:
    model_researcher: str = "gpt-4o-mini"
    model_analyst: str = "gpt-5-mini"
    model_editor: str = "gpt-5-nano"
    search_max_results: int = 5
    use_mock_model: bool = False
    project_root: Path = Path.cwd()

    @property
    def demo_runs_dir(self) -> Path:
        return self.project_root / "demo_runs"

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> "Settings":
        load_dotenv()
        root = project_root or Path.cwd()
        return cls(
            model_researcher=os.getenv("MODEL_RESEARCHER", "gpt-4o-mini"),
            model_analyst=os.getenv("MODEL_ANALYST", "gpt-5-mini"),
            model_editor=os.getenv("MODEL_EDITOR", "gpt-5-nano"),
            search_max_results=int(os.getenv("SEARCH_MAX_RESULTS", "5")),
            use_mock_model=os.getenv("PODCAST_TEAM_USE_MOCK", "0") == "1",
            project_root=root,
        )


def temperature_for_model(model_name: str, default: float) -> float:
    if model_name.startswith("gpt-5"):
        return 1.0
    return default
