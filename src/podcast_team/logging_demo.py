from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class DemoLogger:
    log_path: Path

    @classmethod
    def create(cls, output_dir: Path) -> "DemoLogger":
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = output_dir / f"run_{timestamp}.txt"
        logger = cls(log_path=path)
        logger._write_line(f"Demo run created at {datetime.now().isoformat(timespec='seconds')}")
        return logger

    def log_step_start(self, agent_name: str, summary: str) -> None:
        self._write_line("")
        self._write_line(f"[{agent_name}] START")
        self._write_line(f"Inputs: {summary}")

    def log_tool_call(self, agent_name: str, tool_name: str, arguments: str, result_summary: str) -> None:
        self._write_line(f"[{agent_name}] TOOL {tool_name}")
        self._write_line(f"Args: {arguments}")
        self._write_line(f"Result: {result_summary}")

    def log_step_end(self, agent_name: str, summary: str) -> None:
        self._write_line(f"[{agent_name}] END")
        self._write_line(f"Output: {summary}")

    def annotate(self) -> None:
        self._write_line("")
        self._write_line("# Annotation")
        self._write_line("Researcher is the only agent that calls the search tool.")
        self._write_line("Analyst works only from shared state and does not call tools.")
        self._write_line("Editor uses the internal word_count tool and never touches web search.")

    def _write_line(self, line: str) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")
