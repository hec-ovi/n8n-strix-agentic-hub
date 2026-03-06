"""Normalize Telegram webhook payloads into report requests."""

import re

from src.models.report import ReportRequest, TelegramMessage, TelegramUpdate

REPORT_COMMAND_PREFIX = re.compile(r"^/report(?:@\w+)?\s*", re.IGNORECASE)


def build_report_request_from_telegram(
    update: TelegramUpdate,
    recipient_email: str,
) -> ReportRequest:
    """Convert a Telegram update into the normalized report request shape."""
    message = update.message or update.edited_message or update.channel_post

    if message is None:
        raise ValueError("Telegram update did not include a supported message payload.")

    raw_text = _extract_raw_text(message)
    requester_name = _extract_requester_name(message)

    return ReportRequest(
        requester_name=requester_name,
        requester_channel="telegram",
        recipient_email=recipient_email,
        topic=raw_text[:120] if raw_text else "Telegram report request",
        objective=REPORT_COMMAND_PREFIX.sub("", raw_text).strip()
        or "Summarize the latest Telegram request and turn it into a concise report.",
        tone="executive",
        briefing_notes=[
            "This request originated from Telegram.",
            "Generate a concise PDF artifact and deliver it by email.",
            "If the message begins with /report, ignore the command prefix.",
        ],
    )


def _extract_raw_text(message: TelegramMessage) -> str:
    """Extract the best available text content from a Telegram message."""
    return (message.text or message.caption or "").strip()


def _extract_requester_name(message: TelegramMessage) -> str:
    """Derive a human-readable requester name from the Telegram payload."""
    user = message.from_user
    chat = message.chat

    if user is not None:
        full_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip()
        if full_name:
            return full_name
        if user.username:
            return user.username

    if chat is not None:
        for candidate in [chat.title, chat.username, chat.first_name, chat.last_name]:
            if candidate:
                return candidate

    return "Telegram User"
