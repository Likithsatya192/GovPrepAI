"""Safe JSON parsing helpers for LLM planner outputs."""

from __future__ import annotations

import json
import re
from typing import Any


class LlmJsonParser:
    """Parses JSON arrays from LLM output while tolerating markdown fences."""

    _fence_re = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)

    def strip_markdown_fences(self, text: str) -> str:
        cleaned = text.strip()
        cleaned = self._fence_re.sub("", cleaned).strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```").strip()
        return cleaned

    def parse_array(self, text: str) -> list[dict[str, Any]]:
        cleaned = self.strip_markdown_fences(text)
        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start == -1 or end == -1 or end <= start:
                raise
            value = json.loads(cleaned[start : end + 1])

        if not isinstance(value, list):
            msg = "Expected a JSON array"
            raise ValueError(msg)
        return [item for item in value if isinstance(item, dict)]

