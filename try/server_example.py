#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notify.server import NotifyConfig, main


config = NotifyConfig(
    token="shared-token",
    backend="mail_client",
    mail_client="mail",
    mail_to="kengo.nakada@mat.shimane-u.ac.jp",
)

main(
    config=config,
    host="0.0.0.0",
    port=8000,
)
