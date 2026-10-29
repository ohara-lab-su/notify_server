# notify

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/notify_server/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/notify_server/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fnotify_server-181717?logo=github)](https://github.com/ohara-lab-su/notify_server/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/notify_server/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

A Python package that sends notification requests from a computing machine to a notification server running on your PC via a REST API. The PC then sends an email.

No email account credentials, SMTP passwords, or app passwords are stored on the computing machine. Email is sent exclusively from the PC.

## v0.1.0

Version 0.1.0 introduces `configure()` to make it easier to send notifications from calculation scripts. Server settings can also be passed directly to `NotifyConfig`, rather than being supplied only through environment variables.

### Computing machine

Configure the notification server once before sending notifications.

```python
from notify import configure, notify

configure(
    server_url="http://your-pc-hostname-or-ip:8000/notify",
    token="shared-token",
)

notify("Calculation started")

# calculation()

notify(
    "Calculation finished",
    "Calculation completed successfully.",
)
```

Values set with `configure()` are used as defaults by subsequent calls to `notify()`.

`notify()` returns `True` on success and `False` on failure. By default, failures such as a stopped server, connection problems, timeouts, HTTP errors, or missing configuration do not propagate exceptions to the calculation script.

Specify `strict=True` only when notification failures should raise exceptions.

```python
notify("Calculation finished", strict=True)
```

You can also continue using the `NOTIFY_SERVER_URL` and `NOTIFY_TOKEN` environment variables without calling `configure()`.

### PC-side server

Server settings can be passed directly to `NotifyConfig`.

```python
from notify.server import NotifyConfig, main

config = NotifyConfig(
    token="shared-token",
    backend="mail_client",
    mail_client="mail",
    mail_to="your_account@example.com",
)

main(
    config=config,
    host="0.0.0.0",
    port=8000,
)
```

For fields not explicitly specified in `NotifyConfig`, the corresponding environment variables are used, as before.

If `host` and `port` are omitted from `main()`, the server uses `NOTIFY_HOST` and `NOTIFY_PORT`. If these are also unset, it defaults to `127.0.0.1:8000`.

## Notification methods

### macOS Mail.app

```python
config = NotifyConfig(
    token="shared-token",
    backend="mail_client",
    mail_client="mail",
    mail_to="your_account@example.com",
)
```

Emails are sent by controlling macOS Mail.app through AppleScript.

### Microsoft Outlook

```python
config = NotifyConfig(
    token="shared-token",
    backend="mail_client",
    mail_client="outlook",
    mail_to="your_account@example.com",
)
```

Microsoft Outlook is controlled through AppleScript on macOS and COM (`pywin32`) on Windows.

### SMTP

```python
config = NotifyConfig(
    token="shared-token",
    backend="smtp",
    mail_to="your_account@example.com",
    smtp_host="smtp.example.com",
    smtp_port=587,
    smtp_user="your_account@example.com",
    smtp_password="password-or-app-password",
)
```

The SMTP backend uses STARTTLS and SMTP authentication.

## Shell scripts

When calling notifications from a shell script, set `NOTIFY_SERVER_URL` and `NOTIFY_TOKEN` as environment variables and invoke the package through `python -c`, as before.

```bash
if ./run_calc.sh; then
    python -c 'from notify import notify; notify("OK", "Calculation finished successfully.")'
else
    status=$?
    python -c 'from notify import notify; notify("FAILED", "Calculation failed.")'
    exit "$status"
fi
```

By default, notification failures do not affect the exit status of the calculation command.

## REST API

The REST API remains unchanged.

```text
POST /notify
```

JSON:

```json
{
  "title": "OK",
  "body": "Calculation finished successfully."
}
```

HTTP header:

```text
X-Notify-Token: shared-token
```

## Server configuration options

The following fields can be set directly in `NotifyConfig`:

```text
token
backend
mail_client
mail_to
smtp_host
smtp_port
smtp_user
smtp_password
```

The corresponding existing environment variables are also supported:

```text
NOTIFY_TOKEN
NOTIFY_BACKEND
NOTIFY_MAIL_CLIENT
MAIL_TO
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
NOTIFY_HOST
NOTIFY_PORT
```

Explicitly supplied values take precedence over environment variables.

## Security

The computing machine requires only the notification server URL and a shared token. Email account credentials and SMTP authentication information remain on the PC.

The REST server is not intended to be exposed directly to the internet. For access from external networks, use additional protections such as a VPN, SSH tunnel, firewall, or HTTPS.
