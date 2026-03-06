"""SMTP email sender tool."""

import asyncio
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Protocol

from src.core.exceptions import EmailDeliveryError
from src.core.settings import Settings


class SmtpClientProtocol(Protocol):
    """Protocol for the subset of SMTP client methods used by the sender."""

    def __enter__(self) -> "SmtpClientProtocol": ...

    def __exit__(self, exc_type, exc, tb) -> None: ...

    def ehlo(self) -> tuple[int, bytes]: ...

    def starttls(self) -> tuple[int, bytes]: ...

    def login(self, user: str, password: str) -> tuple[int, bytes]: ...

    def send_message(self, message: EmailMessage) -> None: ...


class EmailSenderTool:
    """Send report emails with attachments."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the email sender with SMTP settings."""
        self._smtp_host = settings.smtp_host
        self._smtp_port = settings.smtp_port
        self._smtp_sender = settings.smtp_sender
        self._smtp_username = settings.smtp_username
        self._smtp_password = settings.smtp_password
        self._smtp_security = settings.smtp_security

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
        with self._build_client() as client:
            client.ehlo()

            if self._smtp_security == "starttls":
                client.starttls()
                client.ehlo()

            if self._smtp_username:
                client.login(self._smtp_username, self._smtp_password or "")

            client.send_message(message)

    def _build_client(self) -> SmtpClientProtocol:
        """Create the appropriate SMTP client for the configured transport mode."""
        if self._smtp_security == "ssl":
            return smtplib.SMTP_SSL(self._smtp_host, self._smtp_port, timeout=30)

        return smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=30)

    def _send_message_for_test(self, recipient_email: str, subject: str, body: str) -> None:
        """Build and send a simple message for unit-level SMTP behavior tests."""
        message = EmailMessage()
        message["From"] = self._smtp_sender
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)
        self._send(message)
