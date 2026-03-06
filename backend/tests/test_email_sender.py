"""Unit tests for SMTP delivery behavior."""

from types import SimpleNamespace

from src.tools.email_sender import EmailSenderTool


class FakeSmtpClient:
    """Minimal SMTP client test double capturing delivery actions."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str | None, str | None]] = []

    def __enter__(self) -> "FakeSmtpClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def ehlo(self) -> tuple[int, bytes]:
        self.events.append(("ehlo", None, None))
        return 250, b"ok"

    def starttls(self) -> tuple[int, bytes]:
        self.events.append(("starttls", None, None))
        return 220, b"ok"

    def login(self, user: str, password: str) -> tuple[int, bytes]:
        self.events.append(("login", user, password))
        return 235, b"ok"

    def send_message(self, message) -> None:
        self.events.append(("send_message", message["To"], message["Subject"]))


def test_email_sender_uses_starttls_and_login(monkeypatch) -> None:
    """Authenticated STARTTLS SMTP should upgrade the connection and log in."""
    client = FakeSmtpClient()

    def fake_smtp(host: str, port: int, timeout: int) -> FakeSmtpClient:
        assert host == "smtp.gmail.com"
        assert port == 587
        assert timeout == 30
        return client

    monkeypatch.setattr("src.tools.email_sender.smtplib.SMTP", fake_smtp)

    settings = SimpleNamespace(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_sender="reports@example.com",
        smtp_username="reports@example.com",
        smtp_password="app-password",
        smtp_security="starttls",
    )
    sender = EmailSenderTool(settings=settings)

    sender._send_message_for_test("recipient@example.com", "Report ready", "Body text")

    assert client.events == [
        ("ehlo", None, None),
        ("starttls", None, None),
        ("ehlo", None, None),
        ("login", "reports@example.com", "app-password"),
        ("send_message", "recipient@example.com", "Report ready"),
    ]


def test_email_sender_uses_ssl_client_without_login(monkeypatch) -> None:
    """SSL SMTP without credentials should skip authentication."""
    client = FakeSmtpClient()

    def fake_smtp_ssl(host: str, port: int, timeout: int) -> FakeSmtpClient:
        assert host == "smtp-relay.gmail.com"
        assert port == 465
        assert timeout == 30
        return client

    monkeypatch.setattr("src.tools.email_sender.smtplib.SMTP_SSL", fake_smtp_ssl)

    settings = SimpleNamespace(
        smtp_host="smtp-relay.gmail.com",
        smtp_port=465,
        smtp_sender="reports@example.com",
        smtp_username=None,
        smtp_password=None,
        smtp_security="ssl",
    )
    sender = EmailSenderTool(settings=settings)

    sender._send_message_for_test("recipient@example.com", "Relay path", "Body text")

    assert client.events == [
        ("ehlo", None, None),
        ("send_message", "recipient@example.com", "Relay path"),
    ]
