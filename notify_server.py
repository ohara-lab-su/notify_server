#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
notify_server.py

計算サーバーなどから HTTP REST API で通知要求を受け取り、Mac 側でメール通知を
実行する簡易通知サーバー。

目的
----
HPC や共通アカウント上の計算ジョブから、メールアカウントやパスワードを使わずに
通知要求だけを送る。通知の実処理は、自分の Mac / 自分のユーザーアカウントで動く
このサーバー側に集約する。

対応する通知方式
----------------
- mail_client
    macOS のメールクライアントを AppleScript 経由で操作してメールを送る。
    NOTIFY_MAIL_CLIENT により、Mail.app または Microsoft Outlook を選ぶ。

- smtp
    SMTP サーバーへ直接接続してメールを送る。
    SMTP_PASSWORD は環境変数から読む。ソースコードには書かない。

環境変数
--------
NOTIFY_TOKEN
    クライアントからの通知要求を認証するための共有トークン。

NOTIFY_BACKEND
    通知方式。"mail_client" または "smtp"。省略時は "mail_client"。

NOTIFY_MAIL_CLIENT
    NOTIFY_BACKEND="mail_client" のときに使う macOS メールクライアント。
    "mail" または "outlook"。省略時は "mail"。

MAIL_TO
    通知メールの送信先。

SMTP_HOST
    SMTP サーバー名。SMTP 使用時のみ必要。

SMTP_PORT
    SMTP ポート番号。SMTP 使用時のみ必要。省略時は 587。

SMTP_USER
    SMTP ユーザー名。SMTP 使用時のみ必要。

SMTP_PASSWORD
    SMTP パスワードまたはアプリパスワード。SMTP 使用時のみ必要。

起動例
------
Mail.app を使う場合

    export NOTIFY_TOKEN="任意の長い文字列"
    export NOTIFY_BACKEND="mail_client"
    export NOTIFY_MAIL_CLIENT="mail"
    export MAIL_TO="your_account@example.com"
    python3 notify_server.py --host 0.0.0.0 --port 8000

Outlook for Mac を使う場合

    export NOTIFY_TOKEN="任意の長い文字列"
    export NOTIFY_BACKEND="mail_client"
    export NOTIFY_MAIL_CLIENT="outlook"
    export MAIL_TO="your_account@example.com"
    python3 notify_server.py --host 0.0.0.0 --port 8000

SMTP を使う場合

    export NOTIFY_TOKEN="任意の長い文字列"
    export NOTIFY_BACKEND="smtp"
    export MAIL_TO="your_account@example.com"
    export SMTP_HOST="smtp.example.com"
    export SMTP_PORT="587"
    export SMTP_USER="your_account@example.com"
    export SMTP_PASSWORD="環境変数にだけ入れる"
    python3 notify_server.py --host 0.0.0.0 --port 8000
"""

import argparse
import os
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
    """通知 API が受け取る JSON 本文。"""

    title: str
    body: str


class NotifyConfig(object):
    """環境変数から読み込む通知サーバー設定。"""

    def __init__(self) -> None:
        """環境変数を読み込み、通知設定を初期化する。"""
        self.token = os.environ.get("NOTIFY_TOKEN", "")
        self.backend = os.environ.get("NOTIFY_BACKEND", "mail_client")
        self.mail_client = os.environ.get("NOTIFY_MAIL_CLIENT", "mail")
        self.mail_to = os.environ.get("MAIL_TO", "")
        self.smtp_host = os.environ.get("SMTP_HOST", "")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")

    def validate_common(self) -> None:
        """全通知方式で必要な設定を検査する。"""
        if self.token == "":
            raise RuntimeError("NOTIFY_TOKEN is not set")

        if self.mail_to == "":
            raise RuntimeError("MAIL_TO is not set")

    def validate_mail_client(self) -> None:
        """macOS メールクライアント通知で必要な設定を検査する。"""
        if self.mail_client == "mail":
            return

        if self.mail_client == "outlook":
            return

        raise RuntimeError("Unknown NOTIFY_MAIL_CLIENT: %s" % self.mail_client)

    def validate_smtp(self) -> None:
        """SMTP 通知で必要な設定を検査する。"""
        if self.smtp_host == "":
            raise RuntimeError("SMTP_HOST is not set")

        if self.smtp_user == "":
            raise RuntimeError("SMTP_USER is not set")

        if self.smtp_password == "":
            raise RuntimeError("SMTP_PASSWORD is not set")


def get_config() -> NotifyConfig:
    """現在の環境変数から通知設定を作成する。"""
    return NotifyConfig()


def escape_applescript_text(text: str) -> str:
    """AppleScript 文字列へ埋め込むために最低限のエスケープを行う。"""
    escaped = text.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"')
    return escaped


def send_by_mail_app(
    config: NotifyConfig,
    title: str,
    body: str,
) -> None:
    """macOS Mail.app を AppleScript で操作してメールを送信する。"""
    subject = escape_applescript_text(title)
    content = escape_applescript_text(body)
    recipient = escape_applescript_text(config.mail_to)

    # Mail.app 側のアカウント設定を使う。
    # そのため、このプログラムには SMTP パスワードを書かない。
    script = """
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"%s", content:"%s", visible:false}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"%s"}
        send
    end tell
end tell
""" % (subject, content, recipient)

    subprocess.check_call(["osascript", "-e", script])


def send_by_outlook_app(
    config: NotifyConfig,
    title: str,
    body: str,
) -> None:
    """macOS Microsoft Outlook を AppleScript で操作してメールを送信する。"""
    subject = escape_applescript_text(title)
    content = escape_applescript_text(body)
    recipient = escape_applescript_text(config.mail_to)

    # Outlook for Mac 側のアカウント設定を使う。
    # Microsoft 365 / Exchange 等の認証情報は Outlook 側に持たせる。
    script = """
tell application "Microsoft Outlook"
    set newMessage to make new outgoing message with properties {subject:"%s", content:"%s"}
    make new recipient at newMessage with properties {email address:{address:"%s"}}
    send newMessage
end tell
""" % (subject, content, recipient)

    subprocess.check_call(["osascript", "-e", script])


def send_by_mail_client(
    config: NotifyConfig,
    title: str,
    body: str,
) -> None:
    """NOTIFY_MAIL_CLIENT に従って macOS メールクライアントから送信する。"""
    config.validate_mail_client()

    if config.mail_client == "mail":
        send_by_mail_app(config, title, body)
        return

    if config.mail_client == "outlook":
        send_by_outlook_app(config, title, body)
        return

    raise RuntimeError("Unknown NOTIFY_MAIL_CLIENT: %s" % config.mail_client)


def send_by_smtp(
    config: NotifyConfig,
    title: str,
    body: str,
) -> None:
    """SMTP サーバーへ直接接続してメールを送信する。"""
    config.validate_smtp()

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = title
    message["From"] = config.smtp_user
    message["To"] = config.mail_to

    with smtplib.SMTP(config.smtp_host, config.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(config.smtp_user, config.smtp_password)
        smtp.send_message(message)


def send_notification(
    config: NotifyConfig,
    title: str,
    body: str,
) -> None:
    """設定された通知方式を使って通知を送信する。"""
    config.validate_common()

    if config.backend == "mail_client":
        send_by_mail_client(config, title, body)
        return

    if config.backend == "smtp":
        send_by_smtp(config, title, body)
        return

    raise RuntimeError("Unknown NOTIFY_BACKEND: %s" % config.backend)


@app.post("/notify")
def notify(
    message: NotifyMessage, x_notify_token: str = Header(default="")
) -> Dict[str, Any]:
    """通知要求を受け取り、認証後に指定された方式で通知する。"""
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


def parse_args() -> argparse.Namespace:
    """サーバー起動用のコマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(
        description="Start notify REST server.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Bind host. Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        type=int,
        help="Bind port. Default: 8000",
    )
    return parser.parse_args()


def main() -> None:
    """通知サーバーを起動する。"""
    os.environ["NOTIFY_TOKEN"] = "任意のアクセストークン"
    os.environ["NOTIFY_BACKEND"] = "mail_client"
    os.environ["NOTIFY_MAIL_CLIENT"] = "mail"
    # os.environ["NOTIFY_MAIL_CLIENT"] = "outlook"
    os.environ["MAIL_TO"] = "kengo.nakada@mat.shimane-u.ac.jp"

    args = parse_args()
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
