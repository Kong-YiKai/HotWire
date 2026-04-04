from __future__ import annotations

import argparse
import unittest
from unittest.mock import patch

from podcast_team.cli import resolve_run_inputs


class PodcastTeamCliTest(unittest.TestCase):
    def test_resolve_run_inputs_uses_terminal_prompts(self) -> None:
        args = argparse.Namespace(
            topic=None,
            tone=None,
            output="output/final_markdown.md",
            mock=False,
            interactive=False,
        )

        with patch(
            "builtins.input",
            side_effect=[
                "2026年新加坡旅游指南",
                "轻松、实用、适合播客讲稿",
                "",
                "n",
            ],
        ):
            topic, tone, output, use_mock = resolve_run_inputs(args)

        self.assertEqual(topic, "2026年新加坡旅游指南")
        self.assertEqual(tone, "轻松、实用、适合播客讲稿")
        self.assertEqual(output, "output/final_markdown.md")
        self.assertFalse(use_mock)

    def test_resolve_run_inputs_keeps_argument_mode(self) -> None:
        args = argparse.Namespace(
            topic="最新的AI新闻",
            tone="专业、清晰、适合博客文章",
            output="output/custom.md",
            mock=True,
            interactive=False,
        )

        topic, tone, output, use_mock = resolve_run_inputs(args)

        self.assertEqual(topic, "最新的AI新闻")
        self.assertEqual(tone, "专业、清晰、适合博客文章")
        self.assertEqual(output, "output/custom.md")
        self.assertTrue(use_mock)


if __name__ == "__main__":
    unittest.main()
