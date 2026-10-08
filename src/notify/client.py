# -*- coding: utf-8 -*-
"""Client-side notification API for compute hosts."""

import os
from typing import Optional

import requests

DEFAULT_TIMEOUT = 10.0

_default_server_url = ""
_default_token = ""
_default_timeout = DEFAULT_TIMEOUT


def configure(
    server_url: str,
    token: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> None:
    """Set default client settings used by notify()."""
    global _default_server_url
    global _default_token
    global _default_timeout

    _default_server_url = server_url
    _default_token = token
    _default_timeout = timeout


class NotifyClient(object):
    """Small HTTP client used from calculation scripts."""

    def __init__(
        self,
        server_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        if server_url is None:
            server_url = _default_server_url
        if server_url == "":
            server_url = os.environ.get("NOTIFY_SERVER_URL", "")

        if token is None:
            token = _default_token
        if token == "":
            token = os.environ.get("NOTIFY_TOKEN", "")

        if timeout is None:
            timeout = _default_timeout

        self.server_url = server_url
        self.token = token
        self.timeout = timeout

    def validate(self) -> None:
        if self.server_url == "":
            raise RuntimeError("NOTIFY_SERVER_URL is not set")
        if self.token == "":
            raise RuntimeError("NOTIFY_TOKEN is not set")

    def send(self, title: str, body: str = "", strict: bool = False) -> bool:
        """Send a notification. Failure is isolated unless strict=True."""
        try:
            self.validate()
            response = requests.post(
                self.server_url,
                json={"title": title, "body": body},
                headers={"X-Notify-Token": self.token},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except Exception:
            if strict:
                raise
            return False


def notify(
    title: str,
    body: str = "",
    strict: bool = False,
    server_url: Optional[str] = None,
    token: Optional[str] = None,
    timeout: Optional[float] = None,
) -> bool:
    """Send a notification with a one-call API."""
    client = NotifyClient(
        server_url=server_url,
        token=token,
        timeout=timeout,
    )
    return client.send(title=title, body=body, strict=strict)
