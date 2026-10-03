from __future__ import annotations

from typing import Any

from keywords.keyword_registry import KeywordRegistry

from .keyword_executor import KeywordExecutor

FIELDS = {"case_id", "step", "keyword", "target", "data", "expected"}


class TestExecutor:
    """Validate a bound case's structure and dispatch its steps in order."""

    def __init__(self, context: Any, registry: KeywordRegistry | None = None):
        self.keyword_executor = KeywordExecutor(context, registry)

    def validate_steps(self, steps: list[dict[str, str]]) -> list[dict[str, str]]:
        if not isinstance(steps, list) or not steps:
            raise ValueError("Kịch bản không có bước")

        first_row = steps[0]
        case_id = first_row.get("case_id") if isinstance(first_row, dict) else None
        canonical_keywords = []

        for index, row in enumerate(steps, 1):
            if not isinstance(row, dict) or set(row) != FIELDS:
                raise ValueError(f"Bước {index}: sai schema")
            if any(not isinstance(value, str) for value in row.values()):
                raise ValueError(f"Bước {index}: dữ liệu phải là chuỗi")
            if not case_id or row["case_id"] != case_id or row["step"] != str(index):
                raise ValueError(f"Bước {index}: sai case_id hoặc thứ tự step")

            try:
                canonical_keywords.append(
                    self.keyword_executor.registry.canonical_name(row["keyword"])
                )
            except (KeyError, TypeError) as exc:
                raise ValueError(f"Bước {index}: {exc}") from exc

        if canonical_keywords[0] != "Navigate":
            raise ValueError("Bước đầu phải là Navigate")
        if not any(keyword.startswith("Verify") for keyword in canonical_keywords):
            raise ValueError("Kịch bản cần ít nhất một bước Verify")

        return steps

    def run(self, steps: list[dict[str, str]]) -> str:
        self.validate_steps(steps)

        for row in steps:
            try:
                self.keyword_executor.execute(row)
            except Exception as error:
                error.add_note(
                    f"Case {row['case_id']}, step {row['step']}, "
                    f"keyword {row['keyword']}"
                )
                raise

        return "PASS"
