# -*- coding: utf-8 -*-
"""REST notification server intended to run on the user's PC."""

import os
import platform
import smtplib
import subprocess
from email.mime.text import MIMEText
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

app = FastAPI(title="Notify Server")


class NotifyMessage(BaseModel):
    title: str
    body: str = ""


class NotifyConfig(object):
    """Server settings loaded from environment variables."""

    def __init__(self) -> None:
        self.token = os.environ.get("NOTIFY_TOKEN", "")
        self.backend = os.environ.get("NOTIFY_BACKEND", "mail_client")
        self.mail_client = os.environ.get("NOTIFY_MAIL_CLIENT", "mail")
        self.mail_to = os.environ.get("MAIL_TO", "")
        self.smtp_host = os.environ.get("SMTP_HOST", "")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")

    def validate_common(self) -> None:
        if self.token == "":
            raise RuntimeError("NOTIFY_TOKEN is not set")
        if self.mail_to == "":
            raise RuntimeError("MAIL_TO is not set")

    def validate_mail_client(self) -> None:
        if self.mail_client not in ("mail", "outlook"):
            raise RuntimeError("Unknown NOTIFY_MAIL_CLIENT: %s" % self.mail_client)
        system = platform.system()
        if self.mail_client == "mail" and system != "Darwin":
            raise RuntimeError("Mail.app backend is available only on macOS")
        if self.mail_client == "outlook" and system not in ("Darwin", "Windows"):
            raise RuntimeError("Outlook backend is available on macOS or Windows")

    def validate_smtp(self) -> None:
        if self.smtp_host == "":
            raise RuntimeError("SMTP_HOST is not set")
        if self.smtp_user == "":
            raise RuntimeError("SMTP_USER is not set")
        if self.smtp_password == "":
            raise RuntimeError("SMTP_PASSWORD is not set")


def get_config() -> NotifyConfig:
    return NotifyConfig()


def escape_applescript_text(text: str) -> str:
    escaped = text.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"')
    return escaped


def send_by_mail_app(config: NotifyConfig, title: str, body: str) -> None:
    subject = escape_applescript_text(title)
    content = escape_applescript_text(body)
    recipient = escape_applescript_text(config.mail_to)
    script = '''
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"%s", content:"%s", visible:false}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"%s"}
        send
    end tell
end tell
''' % (subject, content, recipient)
    subprocess.check_call(["osascript", "-e", script])


def send_by_outlook_mac(config: NotifyConfig, title: str, body: str) -> None:
    subject = escape_applescript_text(title)
    content = escape_applescript_text(body)
    recipient = escape_applescript_text(config.mail_to)
    script = '''
tell application "Microsoft Outlook"
    set newMessage to make new outgoing message with properties {subject:"%s", content:"%s"}
    make new recipient at newMessage with properties {email address:{address:"%s"}}
    send newMessage
end tell
''' % (subject, content, recipient)
    subprocess.check_call(["osascript", "-e", script])


def send_by_outlook_windows(config: NotifyConfig, title: str, body: str) -> None:
    try:
        import win32com.client  # type: ignore
    except ImportError:
        raise RuntimeError("Windows Outlook backend requires pywin32")

    outlook = win32com.client.Dispatch("Outlook.Application")
    message = outlook.CreateItem(0)
    message.To = config.mail_to
    message.Subject = title
    message.Body = body
    message.Send()


def send_by_outlook_app(config: NotifyConfig, title: str, body: str) -> None:
    system = platform.system()
    if system == "Darwin":
        send_by_outlook_mac(config, title, body)
        return
    if system == "Windows":
        send_by_outlook_windows(config, title, body)
        return
    raise RuntimeError("Outlook backend is available on macOS or Windows")


def send_by_mail_client(config: NotifyConfig, title: str, body: str) -> None:
    config.validate_mail_client()
    if config.mail_client == "mail":
        send_by_mail_app(config, title, body)
        return
    if config.mail_client == "outlook":
        send_by_outlook_app(config, title, body)
        return
    raise RuntimeError("Unknown NOTIFY_MAIL_CLIENT: %s" % config.mail_client)


def send_by_smtp(config: NotifyConfig, title: str, body: str) -> None:
    config.validate_smtp()
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = title
    message["From"] = config.smtp_user
    message["To"] = config.mail_to
    with smtplib.SMTP(config.smtp_host, config.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(config.smtp_user, config.smtp_password)
        smtp.send_message(message)


def send_notification(config: NotifyConfig, title: str, body: str) -> None:
    config.validate_common()
    if config.backend == "mail_client":
        send_by_mail_client(config, title, body)
        return
    if config.backend == "smtp":
        send_by_smtp(config, title, body)
        return
    raise RuntimeError("Unknown NOTIFY_BACKEND: %s" % config.backend)


@app.post("/notify")
def receive_notify(
    message: NotifyMessage,
    x_notify_token: str = Header(default=""),
) -> Dict[str, Any]:
    config = get_config()
    if x_notify_token != config.token:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        send_notification(config, message.title, message.body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {
        "ok": True,
        "backend": config.backend,
        "mail_client": config.mail_client,
    }


def main() -> None:
    host = os.environ.get("NOTIFY_HOST", DEFAULT_HOST)
    port = int(os.environ.get("NOTIFY_PORT", str(DEFAULT_PORT)))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
