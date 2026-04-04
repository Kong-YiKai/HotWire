from __future__ import annotations

import argparse
from pathlib import Path

from podcast_team.graph import run_team
from podcast_team.settings import Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the podcast/article multi-agent team.")
    parser.add_argument("--topic", help="Topic to research and write about.")
    parser.add_argument("--tone", help="Desired voice for the final draft.")
    parser.add_argument(
        "--output",
        default="output/final_markdown.md",
        help="Path to write the generated markdown artifact.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use deterministic mock mode instead of live OpenAI calls.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for topic and tone in the terminal before running.",
    )
    return parser


def prompt_for_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("This field is required. Please try again.")


def prompt_with_default(prompt_text: str, default: str) -> str:
    value = input(f"{prompt_text} [{default}]: ").strip()
    return value or default


def prompt_yes_no(prompt_text: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{prompt_text} [{suffix}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def resolve_run_inputs(args: argparse.Namespace) -> tuple[str, str, str, bool]:
    default_tone = "clear and informative"
    if args.interactive or not args.topic:
        print("Podcast Team interactive mode")
        topic = args.topic or prompt_for_non_empty("Enter a topic: ")
        tone = args.tone or prompt_with_default("Enter the desired tone", default_tone)
        output = prompt_with_default("Output path", args.output)
        use_mock = args.mock or prompt_yes_no("Use mock mode instead of live APIs?", default=False)
        return topic, tone, output, use_mock

    return args.topic, args.tone or default_tone, args.output, args.mock


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    topic, tone, output, use_mock = resolve_run_inputs(args)

    settings = Settings.from_env()
    if use_mock:
        settings.use_mock_model = True

    print("Running multi-agent team...")
    state, logger = run_team(topic=topic, tone=tone, settings=settings)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(state["final_markdown"], encoding="utf-8")

    print(f"Saved markdown to {output_path}")
    print(f"Demo log written to {logger.log_path}")
    print("Trace:")
    for entry in state["agent_trace"]:
        print(f"- {entry['agent']}: {entry['summary']}")


if __name__ == "__main__":
    main()
