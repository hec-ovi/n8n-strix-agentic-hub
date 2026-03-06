"""SMTP email sender tool."""

import asyncio
import smtplib
from email.message import EmailMessage
from pathlib import Path

from src.core.exceptions import EmailDeliveryError
from src.core.settings import Settings


class EmailSenderTool:
    """Send report emails with attachments."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the email sender with SMTP settings."""
        self._smtp_host = settings.smtp_host
        self._smtp_port = settings.smtp_port
        self._smtp_sender = settings.smtp_sender

    async def send_report(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        attachment_path: Path,
    ) -> None:
        """Send a report email with a PDF attachment."""
        message = EmailMessage()
        message["From"] = self._smtp_sender
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)
        message.add_attachment(
            attachment_path.read_bytes(),
            maintype="application",
            subtype="pdf",
            filename=attachment_path.name,
        )

        try:
            await asyncio.to_thread(self._send, message)
        except OSError as exc:
            raise EmailDeliveryError(f"Failed to deliver report email: {exc}") from exc

    def _send(self, message: EmailMessage) -> None:
        """Deliver an email message via SMTP."""
        with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=30) as client:
            client.send_message(message)
