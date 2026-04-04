from __future__ import annotations

from typing import Any


def invoke_chat(
    *,
    system_prompt: str,
    user_prompt: str,
    model_name: str,
    temperature: float,
) -> str:
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:  # pragma: no cover - handled at runtime
        raise RuntimeError(
            "langchain-openai is not installed. Run `pip install -e .` first."
        ) from exc

    llm = ChatOpenAI(model=model_name, temperature=temperature)
    response: Any = llm.invoke(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

    content = response.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()
