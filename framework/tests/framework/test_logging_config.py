# ============================================================
# KIỂM TRA LOGGING CONFIGURATION
# Không mở browser, không đọc Excel.
# ============================================================
import logging

import pytest

from utils.logging_config import configure_logging, event_context, resolve_log_level

pytestmark = pytest.mark.framework


def test_log_level_from_environment(monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "DEBUG")
    assert resolve_log_level() == logging.DEBUG


def test_invalid_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "VERBOSE")
    with pytest.raises(ValueError, match="không hợp lệ"):
        resolve_log_level()


def test_log_file_contains_hybrid_context(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "DEBUG")
    # Logger riêng, không đụng logger "hybrid_framework" của cả session.
    logger, log_path = configure_logging(tmp_path, "contract", "hybrid_contract_test")
    logger.info(
        "Hoàn thành bước",
        extra=event_context("LOGIN_01", "3", "SetText", "LoginPage.Username", "PASS"),
    )
    for handler in logger.handlers:
        handler.flush()
    content = log_path.read_text(encoding="utf-8")
    assert (
        "LOGIN_01 | 3 | SetText | LoginPage.Username | PASS | Hoàn thành bước"
        in content
    )
