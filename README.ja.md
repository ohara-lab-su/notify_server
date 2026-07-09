# notify

計算ジョブ終了時に、HPC や共通アカウント側からメールを直接送らず、自分の Mac 上で動く通知サーバーへ REST API で通知要求だけを送るための最小構成です。

計算サーバー側には、メールアカウント、SMTP パスワード、アプリパスワードを置きません。通知の実処理は、自分の Mac / 自分のユーザーアカウントで動く `notify_server.py` が行います。

## 構成

```text
notify_server.py   Mac 側で起動する通知サーバー
notify_client.py   計算サーバー側から通知要求を送るクライアント
notify.sh          計算コマンド終了後に通知するラッパー例
```

## 通知方式

`NOTIFY_BACKEND` で送信方式を選びます。

```text
mail_client   macOS のメールクライアントを使って送信する
smtp          SMTP サーバーへ直接接続して送信する
```

基本は `mail_client` です。`mail_client` の場合は、さらに `NOTIFY_MAIL_CLIENT` で使用するアプリを選びます。

```text
mail       macOS Mail.app を使う
outlook    Microsoft Outlook for Mac を使う
```

Mail.app または Outlook 側にメールアカウントを設定しておけば、プログラム中に SMTP パスワードを書かずに済みます。

SMTP を使う場合も、パスワードはソースコードには書かず、環境変数 `SMTP_PASSWORD` で渡します。

## インストール

Mac 側で必要な Python パッケージです。

```bash
python3 -m pip install fastapi uvicorn pydantic requests
```

計算サーバー側は、クライアントだけなら `requests` があれば動きます。

```bash
python3 -m pip install requests
```

## Mac 側: Mail.app でサーバー起動

```bash
export NOTIFY_TOKEN="任意の長い文字列"
export NOTIFY_BACKEND="mail_client"
export NOTIFY_MAIL_CLIENT="mail"
export MAIL_TO="your_account@example.com"

python3 notify_server.py --host 0.0.0.0 --port 8000
```

`MAIL_TO` には通知を受け取るメールアドレスを指定します。

初回実行時、macOS が Terminal や Python から Mail.app を操作する許可を求める場合があります。その場合は許可してください。

## Mac 側: Outlook for Mac でサーバー起動

```bash
export NOTIFY_TOKEN="任意の長い文字列"
export NOTIFY_BACKEND="mail_client"
export NOTIFY_MAIL_CLIENT="outlook"
export MAIL_TO="your_account@example.com"

python3 notify_server.py --host 0.0.0.0 --port 8000
```

Outlook for Mac 側に送信用アカウントが設定されている必要があります。Microsoft 365 / Exchange の認証情報は Outlook 側に持たせます。通知プログラム側にはパスワードを書きません。

初回実行時、macOS が Terminal や Python から Microsoft Outlook を操作する許可を求める場合があります。その場合は許可してください。

## Mac 側: SMTP でサーバー起動

```bash
export NOTIFY_TOKEN="任意の長い文字列"
export NOTIFY_BACKEND="smtp"
export MAIL_TO="your_account@example.com"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="your_account@example.com"
export SMTP_PASSWORD="環境変数にだけ入れる"

python3 notify_server.py --host 0.0.0.0 --port 8000
```

`SMTP_PASSWORD` はソースコード、README、シェルスクリプトには書かないでください。必要な実行環境だけで `export` します。

## 計算サーバー側: クライアント実行

```bash
export NOTIFY_SERVER_URL="http://your-mac-hostname-or-ip:8000/notify"
export NOTIFY_TOKEN="Mac 側と同じ文字列"

python3 notify_client.py "OK" "Calculation finished successfully."
```

## 計算ジョブへの組み込み例

`notify.sh` は、`run_calc.sh` の終了状態に応じて通知を送る例です。

```bash
export NOTIFY_SERVER_URL="http://your-mac-hostname-or-ip:8000/notify"
export NOTIFY_TOKEN="Mac 側と同じ文字列"

bash notify.sh
```

成功時は `OK`、失敗時は `FAILED` を送ります。

## API

通知サーバーは次の API を持ちます。

```text
POST /notify
```

JSON 本文です。

```json
{
  "title": "OK",
  "body": "Calculation finished successfully."
}
```

HTTP ヘッダーに共有トークンを付けます。

```text
X-Notify-Token: 任意の長い文字列
```

## 注意

この構成は、簡単な個人用通知を目的としたものです。
インターネットへ直接公開する前提ではありません。外部から到達できる場所で使う場合は、
VPN、SSH トンネル、ファイアウォール、HTTPS 化などを別途検討してください。
