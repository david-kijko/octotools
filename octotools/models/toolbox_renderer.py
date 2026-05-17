"""Render toolbox metadata as text or committed PNG tool-card attachments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Union

ToolboxPayload = Union[str, List[Union[str, bytes]]]

_CARD_DIR = Path(__file__).resolve().parents[1] / "tools" / "_cards"


def _filtered_metadata(toolbox_metadata: Dict[str, Any], available_tools: List[str]) -> Dict[str, Any]:
    return {tool: toolbox_metadata[tool] for tool in available_tools if tool in toolbox_metadata}


def _card_path(tool_name: str) -> Path:
    return _CARD_DIR / f"{tool_name}.png"


def get_toolbox_payload(
    toolbox_metadata: Dict[str, Any],
    available_tools: List[str],
    mode: Literal["text", "image"] = "text",
) -> ToolboxPayload:
    """Return text metadata for text mode or PNG tool-card attachments for image mode."""
    if mode == "text":
        return json.dumps(_filtered_metadata(toolbox_metadata, available_tools), indent=2, default=str)
    if mode != "image":
        raise ValueError(f"Unsupported toolbox mode: {mode}")

    payload: List[Union[str, bytes]] = []
    for tool_name in available_tools:
        card = _card_path(tool_name)
        if not card.exists():
            raise FileNotFoundError(f"Missing image tool card for {tool_name}: {card}")
        payload.append(f"Tool card for {tool_name} follows. Use this PNG as the tool metadata.")
        payload.append(card.read_bytes())
    return payload


def describe_toolbox_payload(payload: ToolboxPayload) -> str:
    if isinstance(payload, str):
        return payload
    count = sum(1 for item in payload if isinstance(item, bytes))
    return f"{count} PNG tool-card image attachment(s) supplied after this prompt."
