#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
notify_client.py

計算ジョブ終了時に通知サーバーへ HTTP POST を送る最小クライアント。

目的
----
HPC や共通アカウント側にはメールアカウント、SMTP パスワード、アプリパスワードを
置かない。計算終了後に通知サーバーへ title/body だけを送る。

環境変数
--------
NOTIFY_SERVER_URL
    通知サーバーの URL。例: http://192.168.1.10:8000/notify

NOTIFY_TOKEN
    通知サーバー側の NOTIFY_TOKEN と同じ共有トークン。

使用例
------
    export NOTIFY_SERVER_URL="http://your-mac:8000/notify"
    export NOTIFY_TOKEN="任意の長い文字列"
    python3 notify_client.py "OK" "Calculation finished successfully."
"""

import argparse
import os
from typing import Dict

import requests

DEFAULT_TIMEOUT = 10


class ClientConfig(object):
    """通知クライアントの設定。"""

    def __init__(self) -> None:
        """環境変数から通知先 URL と共有トークンを読み込む。"""
        self.server_url = os.environ.get(
            "NOTIFY_SERVER_URL",
            "",
        )
        self.token = os.environ.get(
            "NOTIFY_TOKEN",
            "",
        )

    def validate(self) -> None:
        """通知送信に必要な設定を検査する。"""
        if self.server_url == "":
            raise RuntimeError("NOTIFY_SERVER_URL is not set")

        if self.token == "":
            raise RuntimeError("NOTIFY_TOKEN is not set")


def notify(
    config: ClientConfig,
    title: str,
    body: str,
) -> None:
    """通知サーバーへ title/body を送信する。"""
    config.validate()

    payload = {
        "title": title,
        "body": body,
    }

    headers = {
        "X-Notify-Token": config.token,
    }

    response = requests.post(
        config.server_url,
        json=payload,
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()


def parse_args() -> argparse.Namespace:
    """コマンドライン引数から通知タイトルと本文を取得する。"""
    parser = argparse.ArgumentParser(
        description="Send notification to notify server.",
    )
    parser.add_argument(
        "title",
        help="Notification title",
    )
    parser.add_argument(
        "body",
        help="Notification body",
    )
    return parser.parse_args()


def main() -> None:
    """通知クライアントを実行する。"""
    args = parse_args()
    config = ClientConfig()

    config.server_url = "http://127.0.0.1:8000/notify"
    config.token = "任意のアクセストークン"

    notify(config, args.title, args.body)


if __name__ == "__main__":
    main()
