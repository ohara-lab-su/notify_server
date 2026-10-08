# notify

計算機から自分の PC 上の通知サーバーへ REST API で通知要求を送り、PC
側からメールを送信する Python パッケージです。

計算機側にはメールアカウント、SMTP
パスワード、アプリパスワードを置きません。メール送信は PC
側だけで行います。

## v0.1.0

v0.1.0 では、計算スクリプトから通知を簡単に呼び出せるように
`configure()` を追加しました。また、サーバー設定を環境変数だけでなく
`NotifyConfig` へ直接指定できるようにしました。

### 計算機側

最初に一度だけ通知サーバーを設定します。

``` python
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

`configure()` で設定した値は、その後の `notify()`
で既定値として使用されます。

`notify()` は成功時に `True`、失敗時に `False`
を返します。デフォルトでは、サーバー停止、通信不能、timeout、HTTP
エラー、設定不足などが発生しても例外を計算側へ伝播しません。

通知失敗を例外として扱う場合だけ `strict=True` を指定します。

``` python
notify("Calculation finished", strict=True)
```

`configure()` を使用せず、従来どおり `NOTIFY_SERVER_URL` と
`NOTIFY_TOKEN` の環境変数を使用することもできます。

### PC 側サーバー

サーバー設定は `NotifyConfig` へ直接渡せます。

``` python
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

`NotifyConfig`
に値を指定しなかった項目については、従来どおり環境変数が使用されます。

`main()` の `host` / `port` を省略した場合も、`NOTIFY_HOST` /
`NOTIFY_PORT` を参照し、未設定なら `127.0.0.1:8000` を使用します。

## 通知方式

### macOS Mail.app

``` python
config = NotifyConfig(
    token="shared-token",
    backend="mail_client",
    mail_client="mail",
    mail_to="your_account@example.com",
)
```

AppleScript で macOS Mail.app を操作してメールを送信します。

### Microsoft Outlook

``` python
config = NotifyConfig(
    token="shared-token",
    backend="mail_client",
    mail_client="outlook",
    mail_to="your_account@example.com",
)
```

macOS では AppleScript、Windows では COM (`pywin32`) を使用して
Microsoft Outlook を操作します。

### SMTP

``` python
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

SMTP は STARTTLS と SMTP 認証を使用します。

## Shell スクリプト

Shell から使用する場合は、従来どおり `NOTIFY_SERVER_URL` と
`NOTIFY_TOKEN` を環境変数で与えれば `python -c` から呼び出せます。

``` bash
if ./run_calc.sh; then
    python -c 'from notify import notify; notify("OK", "Calculation finished successfully.")'
else
    status=$?
    python -c 'from notify import notify; notify("FAILED", "Calculation failed.")'
    exit "$status"
fi
```

デフォルトでは通知失敗が計算コマンドの終了状態へ影響しません。

## REST API

REST API は従来と同じです。

``` text
POST /notify
```

JSON:

``` json
{
  "title": "OK",
  "body": "Calculation finished successfully."
}
```

HTTP header:

``` text
X-Notify-Token: shared-token
```

## サーバー設定項目

`NotifyConfig` で直接指定できる項目は次のとおりです。

``` text
token
backend
mail_client
mail_to
smtp_host
smtp_port
smtp_user
smtp_password
```

対応する従来の環境変数も使用できます。

``` text
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

直接指定した値は環境変数より優先されます。

## セキュリティ

計算機側に必要なのは通知サーバー URL
と共有トークンだけです。メールアカウントや SMTP 認証情報は PC
側に置きます。

REST
サーバーをインターネットへ直接公開することは前提としていません。外部ネットワークから利用する場合は、VPN、SSH
トンネル、ファイアウォール、HTTPS 等を別途使用してください。
