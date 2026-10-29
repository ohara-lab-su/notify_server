# Installation and usage

Install with `pip install notify-frame`. Install the bundled example scripts into the current directory with `notify_server install`, or replace existing copies with `notify_server install --force`.

## Compute host

```python
from notify import configure, notify
configure(server_url="http://your-pc:8000/notify", token="shared-token")
notify("Calculation started")
notify("Calculation finished", "Completed successfully")
```

`notify()` returns `False` on failure without raising by default; use `strict=True` to propagate failures. Environment variables `NOTIFY_SERVER_URL` and `NOTIFY_TOKEN` are also supported.

## PC-side server

```python
from notify.server import NotifyConfig, main
config = NotifyConfig(token="shared-token", backend="mail_client", mail_client="mail", mail_to="your_account@example.com")
main(config=config, host="0.0.0.0", port=8000)
```

The server supports macOS Mail.app, Microsoft Outlook (macOS/Windows), and SMTP with STARTTLS. The REST endpoint is `POST /notify`, accepting `title` and `body` JSON fields with an `X-Notify-Token` header. Do not expose the HTTP server directly to the public internet.
