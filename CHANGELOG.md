# CHANGELOG

## v0.1.0

v0.0.0 の通知方式と REST API を維持しながら、計算スクリプトへ組み込みやすい Python パッケージへ変更。

### Added

- PyPI / pip 配布用の `pyproject.toml` を追加。
- `from notify import notify` で利用できる公開 API を追加。
- `NotifyClient` クラスを追加。
- `notify(title)` のように本文を省略できるようにした。
- `notify()` / `NotifyClient.send()` は成功時 `True`、失敗時 `False` を返す。
- `strict=True` を指定した場合のみ、通知失敗の例外を呼び出し元へ伝播する機能を追加。
- Windows の Microsoft Outlook 送信に対応。Windows Outlook 使用時のみ `pywin32` が必要。
- `notify-server` エントリポイントを追加。
- サーバーの bind host / port を `NOTIFY_HOST` / `NOTIFY_PORT` で指定可能にした。

### Changed

- クライアントを単独実行スクリプト中心の構成から、Python から直接 import するモジュール中心の構成へ変更。
- 通知サーバーが停止している場合、通信不能、timeout、HTTP エラー、クライアント設定不足などが発生しても、デフォルトでは計算側へ例外を伝播しない仕様に変更。
- サーバー起動時の `argparse` を廃止。
- macOS Outlook の実装を Windows Outlook と共通の Outlook backend として整理。
- examples の Python / shell 組み込み例を v0.1.0 API に更新。

### Preserved from v0.0.0

- `POST /notify` REST API。
- `X-Notify-Token` による共有トークン認証。
- `title` / `body` の通知データ。
- `NOTIFY_SERVER_URL` / `NOTIFY_TOKEN` によるクライアント設定。
- `NOTIFY_BACKEND=mail_client` / `smtp`。
- macOS Mail.app の AppleScript 送信。
- Microsoft Outlook for Mac の AppleScript 送信。
- SMTP / STARTTLS / SMTP 認証。
- `MAIL_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` の環境変数設定。

## v0.0.0

初期版。

- 計算機から REST API で PC 上の通知サーバーへ通知要求を送信。
- メールアカウントや SMTP パスワードを計算機側へ置かない構成。
- macOS Mail.app、Microsoft Outlook for Mac、SMTP に対応。
