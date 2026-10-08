#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notify import configure, notify

configure(
    server_url="http://127.0.0.1:8000/notify",
    token="shared-token",
)

# notify("Calculation started")

# calculation()

notify(
    "Calculation finished",
    "Calculation completed successfully.",
)
