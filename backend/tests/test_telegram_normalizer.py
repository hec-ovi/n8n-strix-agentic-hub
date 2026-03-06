"""Tests for Telegram webhook normalization."""

from src.lib.telegram_normalizer import build_report_request_from_telegram
from src.models.report import TelegramUpdate


def test_build_report_request_from_telegram_strips_report_command() -> None:
    """Telegram /report commands should be normalized into report requests."""
    update = TelegramUpdate.model_validate(
        {
            "update_id": 10001,
            "message": {
                "message_id": 42,
                "text": "/report Build a crisp summary of n8n queue mode",
                "from": {
                    "id": 9001,
                    "first_name": "Telegram",
                    "last_name": "Tester",
                    "username": "telegram_tester",
                },
                "chat": {
                    "id": 9001,
                    "type": "private",
                    "username": "telegram_tester",
                },
            },
        }
    )

    request = build_report_request_from_telegram(
        update=update,
        recipient_email="reports@example.com",
    )

    assert request.requester_name == "Telegram Tester"
    assert request.requester_channel == "telegram"
    assert str(request.recipient_email) == "reports@example.com"
    assert request.objective == "Build a crisp summary of n8n queue mode"
    assert request.topic.startswith("/report Build a crisp summary")


def test_build_report_request_from_telegram_requires_message_payload() -> None:
    """Unsupported Telegram updates should be rejected early."""
    update = TelegramUpdate.model_validate({"update_id": 10002})

    try:
        build_report_request_from_telegram(
            update=update,
            recipient_email="reports@example.com",
        )
    except ValueError as exc:
        assert "supported message payload" in str(exc)
    else:
        raise AssertionError("Expected Telegram normalization to reject empty updates.")
