from __future__ import annotations

from typing import Any

import allure

from keywords.keyword_registry import KeywordRegistry
from utils.error_classifier import classify_exception
from utils.logging_config import event_context, get_logger

from .keyword_executor import KeywordExecutor

FIELDS = {"case_id", "step", "keyword", "target", "data", "expected"}
SENSITIVE = ("password",)


def _mask(row: dict[str, str]) -> str:
    """Không để mật khẩu lọt vào log/báo cáo."""
    if any(word in row["target"].lower() for word in SENSITIVE) and row["data"]:
        return "***"
    return row["data"]


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
        log = get_logger()
        case_id = steps[0]["case_id"]
        log.info(
            "Bắt đầu test case",
            extra=event_context(tc_id=case_id, action="execute_case", result="START"),
        )

        for row in steps:
            ctx = event_context(
                case_id, row["step"], row["keyword"], row["target"], "START"
            )
            log.info("Bắt đầu bước", extra=ctx)

            title = f"{case_id} | Step {row['step']} | {row['keyword']} | {row['target'] or '-'}"
            data = _mask(row)
            if data:
                title += f" | {data}"

            with allure.step(title):
                try:
                    result = self.keyword_executor.execute(row)
                except Exception as error:
                    category = classify_exception(error)
                    error.add_note(
                        f"Case {case_id}, step {row['step']}, keyword {row['keyword']}, "
                        f"target {row['target'] or '-'}, category {category}"
                    )
                    log.exception(
                        f"Bước thất bại; category={category}",
                        extra={**ctx, "result": "FAIL"},
                    )
                    allure.attach(
                        category, "error-category", allure.attachment_type.TEXT
                    )
                    raise
                log.info(
                    getattr(result, "message", "Hoàn thành bước"),
                    extra={**ctx, "result": "PASS"},
                )

        log.info(
            "Hoàn thành test case",
            extra=event_context(tc_id=case_id, action="execute_case", result="PASS"),
        )
        return "PASS"
