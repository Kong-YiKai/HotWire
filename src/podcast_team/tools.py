from __future__ import annotations

from typing import Any


def search_web(query: str, max_results: int = 5, use_mock: bool = False) -> list[dict[str, str]]:
    if use_mock:
        return [
            {
                "title": "Mock source 1",
                "url": "https://example.com/mock-source-1",
                "snippet": f"Synthetic background notes for {query}.",
            },
            {
                "title": "Mock source 2",
                "url": "https://example.com/mock-source-2",
                "snippet": f"Mock trend summary related to {query}.",
            },
            {
                "title": "Mock source 3",
                "url": "https://example.com/mock-source-3",
                "snippet": f"Mock commentary and context about {query}.",
            },
        ][:max_results]

    try:
        from ddgs import DDGS
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError("ddgs is not installed. Run `pip install -e .` first.") from exc

    results: list[dict[str, str]] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            normalized = _normalize_search_item(item)
            if normalized:
                results.append(normalized)
    return results


def _normalize_search_item(item: dict[str, Any]) -> dict[str, str] | None:
    title = str(item.get("title") or "").strip()
    url = str(item.get("href") or item.get("url") or "").strip()
    snippet = str(item.get("body") or item.get("snippet") or "").strip()
    if not url:
        return None
    return {
        "title": title or "Untitled source",
        "url": url,
        "snippet": snippet or "No summary returned.",
    }


def format_search_results(results: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        lines.append(
            f"{index}. {result['title']}\nURL: {result['url']}\nSnippet: {result['snippet']}"
        )
    return "\n\n".join(lines)


def word_count(text: str) -> int:
    return len([token for token in text.split() if token.strip()])
