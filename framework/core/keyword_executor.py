from __future__ import annotations

from typing import Any

from keywords.keyword_registry import KeywordRegistry, build_default_registry


class KeywordExecutor:
    """Resolve a keyword and invoke its handler for one step."""

    def __init__(self, context: Any, registry: KeywordRegistry | None = None):
        self.context = context
        self.registry = registry if registry is not None else build_default_registry()

    def execute(self, row: dict[str, str]) -> Any:
        handler = self.registry.resolve(row["keyword"])
        return handler(
            row["target"],
            row["data"],
            row["expected"],
            self.context,
        )
