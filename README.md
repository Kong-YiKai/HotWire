# Podcast Team

Podcast Team is a small multi-agent Python project that turns a user topic into a polished Markdown article or short podcast script. It uses a sequential LangGraph workflow with three distinct agents, explicit shared state, and different tool permissions per agent.

## Overview

- `Researcher` gathers fresh information with web search and writes research notes plus source URLs into shared state.
- `Analyst` reads only the shared state, organizes the findings into structured bullets, and records factual caveats.
- `ChiefEditor` turns those bullets into the final Markdown artifact and uses an internal `word_count` tool to summarize draft size.

The graph follows a linear flow: `research -> analyze -> edit`.

## Prerequisites

- Python 3.11 or newer
- An OpenAI API key in `.env` for live runs
- Internet access for live search runs

Mock mode is included for offline demos, testing, and grading dry runs.

## Setup

1. Create and activate a virtual environment.
2. Install the package in editable mode.
3. Copy `.env.example` to `.env`.
4. Add `OPENAI_API_KEY` and adjust any optional model overrides.

Example setup:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

## Run

Interactive terminal Q&A mode:

```powershell
python -m podcast_team
```

The CLI will prompt you for:

- topic
- tone
- output path
- whether to use mock mode

CLI entrypoint:

```powershell
python -m podcast_team --topic "AI agents in education" --tone "friendly podcast script"
```

Script entrypoint:

```powershell
python scripts/run.py --topic "Climate tech in 2026" --tone "clear and analytical"
```

Mock/offline run:

```powershell
python -m podcast_team --topic "AI agents in education" --tone "friendly podcast script" --mock
```

You can also force prompts even when you want to keep some flags on the command line:

```powershell
python -m podcast_team --interactive
```

By default, the final Markdown is written to `output/final_markdown.md`. Each run also creates a timestamped text log in `demo_runs/`.

## Architecture

```mermaid
flowchart LR
  user[User topic input]
  graph[LangGraph orchestrator]
  r[Researcher]
  a[Analyst]
  e[Chief Editor]
  s[Shared State]
  search[web_search]
  wc[word_count]
  user --> graph
  graph --> r
  r --> search
  r --> s
  s --> a
  a --> s
  s --> e
  e --> wc
  e --> s
```

Shared state fields:

- `topic`
- `tone`
- `raw_research`
- `structured_bullets`
- `warnings`
- `source_urls`
- `final_markdown`
- `agent_trace`

## Agents And Tools

| Agent | Role | Allowed tools | Writes to state |
| --- | --- | --- | --- |
| Researcher | Gather recent source-backed notes | `web_search` only | `raw_research`, `source_urls`, `agent_trace` |
| Analyst | Structure findings and identify caveats | None | `structured_bullets`, `warnings`, `agent_trace` |
| ChiefEditor | Produce final Markdown draft | `word_count` only | `final_markdown`, `agent_trace` |

## Demo Log

Each run creates a log file under `demo_runs/` with:

- step start and end markers
- tool invocations and summarized arguments
- short summaries of what each agent wrote to shared state
- a short annotation block that highlights coordination and permission boundaries

A sample deliverable log is checked in at `docs/demo_run_example.txt`.

## Integration Check

A lightweight integration test lives in `tests/test_integration.py`. It runs the full three-agent workflow in mock mode and verifies that:

- the final Markdown is generated
- three trace entries are recorded
- a demo log file is created
- the researcher writes source URLs into shared state

Run it with:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Submission Zip Instructions

Use `docs/zip_checklist.md` before packaging the project. Exclude local environments, caches, and `.env`, but include the source code, README, tests, and the sample demo log.

