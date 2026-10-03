from typing import Any

from .executor_test import TestExecutor


class KeywordEngine(TestExecutor):
    """Compatibility facade for the TestExecutor pipeline."""

    def __init__(self, context: Any, registry=None):
        super().__init__(context, registry)
