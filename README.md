# notify

計算機から自分の PC 上の通知サーバーへ REST API で通知要求を送り、PC 側からメールを送信する Python パッケージです。

計算機側にはメールアカウント、SMTP パスワード、アプリパスワードを置きません。メール送信は自分の PC 側だけで行います。

## v0.1.0 の基本形

計算スクリプト側は次の 1 行で通知できます。

```python
from notify import notify

notify("Calculation finished")
```

本文も指定できます。

```python
notify("Calculation finished", "D490 calculation completed successfully.")
```

通知は計算本体に対する補助機能です。通知サーバーが停止している、ネットワークが切れている、timeout、設定不足、HTTP エラーなどが発生しても、デフォルトでは例外を計算側へ伝播しません。

```python
result = notify("Calculation finished")
```

成功時は `True`、失敗時は `False` です。戻り値を使わなければ、そのまま無視できます。

通知失敗を例外として扱いたい場合だけ `strict=True` を指定します。

```python
notify("Calculation finished", strict=True)
```

## 構成

```text
notify/
    __init__.py
    client.py       計算機側の通知 API
    server.py       PC 側の REST サーバーとメール送信
examples/
    notify_example.py
    notify.sh
pyproject.toml      PyPI / pip パッケージ定義
README.ja.md
CHANGELOG.md
```

`pyproject.toml` は通知設定ファイルではありません。PyPI / pip 配布用のパッケージ定義です。

## インストール

計算機側はクライアント機能だけなら通常のインストールで十分です。

```bash
pip install notify
```

ソースツリーから確認する場合は次のようにインストールできます。

```bash
pip install .
```

PC 側で通知サーバーも使用する場合は server extra を追加します。

```bash
pip install '.[server]'
```

Windows の Microsoft Outlook を使う場合はさらに次を使用します。

```bash
pip install '.[server,windows-outlook]'
```

## 計算機側の設定

v0.0.0 と同じ環境変数を使用します。

```bash
export NOTIFY_SERVER_URL="http://your-pc-hostname-or-ip:8000/notify"
export NOTIFY_TOKEN="PC 側と同じ共有トークン"
```

Python 側は次だけです。

```python
from notify import notify

notify("Calculation started")

# 計算処理

notify("Calculation finished", "Calculation completed successfully.")
```

必要であれば URL、token、timeout を直接指定することもできます。

```python
notify(
    "Calculation finished",
    server_url="http://127.0.0.1:8000/notify",
    token="shared-token",
    timeout=5.0,
)
```

複数回通知する場合は `NotifyClient` を明示的に生成することもできます。

```python
from notify import NotifyClient

client = NotifyClient()
client.send("Calculation started")
client.send("Step 1 finished")
client.send("Calculation finished")
```

通常は単純な `notify()` だけで構いません。

## PC 側の通知方式

メール送信はすべて PC 側の責務です。計算機側はどの方式でメールが送られるかを知る必要がありません。

`NOTIFY_BACKEND` で送信方式を選択します。

```text
mail_client   PC に設定済みのメールクライアントを使う
smtp          SMTP サーバーへ直接接続する
```

`mail_client` の場合は `NOTIFY_MAIL_CLIENT` を指定します。

```text
mail       macOS Mail.app
outlook    Microsoft Outlook
```

`outlook` は実行 OS に応じて自動的に方式を切り替えます。

```text
macOS      AppleScript で Microsoft Outlook for Mac を操作
Windows    COM で Microsoft Outlook を操作
```

### macOS Mail.app

```bash
export NOTIFY_TOKEN="任意の長い文字列"
export NOTIFY_BACKEND="mail_client"
export NOTIFY_MAIL_CLIENT="mail"
export MAIL_TO="your_account@example.com"
export NOTIFY_HOST="0.0.0.0"
export NOTIFY_PORT="8000"

notify-server
```

Mail.app 側のアカウント設定を利用するため、SMTP パスワードを notify に保存する必要はありません。

### Microsoft Outlook for Mac

```bash
export NOTIFY_TOKEN="任意の長い文字列"
export NOTIFY_BACKEND="mail_client"
export NOTIFY_MAIL_CLIENT="outlook"
export MAIL_TO="your_account@example.com"
export NOTIFY_HOST="0.0.0.0"
export NOTIFY_PORT="8000"

notify-server
```

Outlook for Mac 側に設定済みのアカウントを利用します。

### Microsoft Outlook for Windows

Windows 側では `pywin32` を使用してインストール済み Outlook を操作します。

```text
NOTIFY_TOKEN       共有トークン
NOTIFY_BACKEND     mail_client
NOTIFY_MAIL_CLIENT outlook
MAIL_TO            通知先メールアドレス
NOTIFY_HOST        0.0.0.0
NOTIFY_PORT        8000
```

サーバー起動は次です。

```text
notify-server
```

Outlook にメールアカウントが設定済みである必要があります。

### SMTP

```bash
export NOTIFY_TOKEN="任意の長い文字列"
export NOTIFY_BACKEND="smtp"
export MAIL_TO="your_account@example.com"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="your_account@example.com"
export SMTP_PASSWORD="password-or-app-password"
export NOTIFY_HOST="0.0.0.0"
export NOTIFY_PORT="8000"

notify-server
```

SMTP は STARTTLS を使用します。`SMTP_PASSWORD` はソースコードへ書かず、実行環境の環境変数で与えます。

## サーバー設定

v0.1.0 でも設定ファイルは使用せず、環境変数を使用します。

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

`NOTIFY_HOST` のデフォルトは `127.0.0.1`、`NOTIFY_PORT` のデフォルトは `8000` です。

## Shell スクリプトへの組み込み

`examples/notify.sh` に例があります。

```bash
if ./run_calc.sh; then
    python -c 'from notify import notify; notify("OK", "Calculation finished successfully.")'
else
    status=$?
    python -c 'from notify import notify; notify("FAILED", "Calculation failed.")'
    exit "$status"
fi
```

通知サーバーへの接続に失敗しても `notify()` 自身はデフォルトでは例外を外へ出さないため、通知失敗によって計算処理の結果を変更しません。

## REST API

v0.0.0 と同じ API を維持しています。

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

## セキュリティ

メールアカウントや SMTP 認証情報を計算機へ置かないことがこの構成の目的です。計算機側に必要なのは通知サーバー URL と共有トークンだけです。

この REST サーバーをインターネットへ直接公開することは前提としていません。外部ネットワークから使用する場合は VPN、SSH トンネル、ファイアウォール、HTTPS 等を別途使用してください。
