from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from podcast_team.graph import run_team
from podcast_team.settings import Settings


class PodcastTeamIntegrationTest(unittest.TestCase):
    def test_mock_pipeline_runs_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(project_root=Path(temp_dir), use_mock_model=True)
            state, logger = run_team(
                topic="AI agents in education",
                tone="friendly podcast script",
                settings=settings,
            )

            self.assertIn("# AI agents in education", state["final_markdown"])
            self.assertEqual(len(state["agent_trace"]), 3)
            self.assertTrue(logger.log_path.exists())
            self.assertTrue(state["source_urls"])


if __name__ == "__main__":
    unittest.main()
