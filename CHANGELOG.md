# CHANGELOG

## v0.1.1

- LICENSE 追加

## v0.1.0

v0.0.0 の REST 通知方式を維持しながら、Python
スクリプトへ組み込みやすい構成へ変更。

### Added

-   クライアントに `configure(server_url, token, timeout)` を追加。
    -   通知サーバー URL、共有トークン、timeout を最初に一度設定可能。
    -   設定後は `notify()` だけで通知可能。
-   `NotifyClient` を追加。
-   `notify(title, body="", strict=False, ...)` を追加。
    -   `body` は省略可能。
    -   成功時は `True`、失敗時は `False`。
    -   `strict=True` の場合のみ通知失敗の例外を呼び出し元へ伝播。
-   サーバーに `NotifyConfig` を追加。
    -   token、backend、mail client、送信先、SMTP 設定を Python
        から直接指定可能。
    -   直接指定されていない項目は従来の環境変数から取得。
-   `main(config=..., host=..., port=...)` によるサーバー起動に対応。
-   Windows の Microsoft Outlook 送信に対応。
    -   Windows では `pywin32` による COM を使用。

### Changed

-   クライアントは、通知先を毎回 `notify()` へ渡す必要がない構成へ変更。
-   通知失敗はデフォルトで計算処理へ例外を伝播しない仕様へ変更。
-   サーバー設定は環境変数だけでなく `NotifyConfig`
    への直接指定を優先できるように変更。
-   `main()` の `host` / `port` は直接指定可能。
    -   未指定の場合は `NOTIFY_HOST` / `NOTIFY_PORT` を使用。
    -   環境変数も未設定の場合は `127.0.0.1:8000` を使用。
-   macOS / Windows の Outlook を共通の `outlook` mail client
    として扱う構成に整理。

### Preserved

-   `POST /notify` REST API。
-   `X-Notify-Token` による共有トークン認証。
-   `title` / `body` の通知データ。
-   `NOTIFY_SERVER_URL` / `NOTIFY_TOKEN` によるクライアント設定。
-   `NOTIFY_BACKEND=mail_client` / `smtp`。
-   macOS Mail.app の AppleScript 送信。
-   Microsoft Outlook for Mac の AppleScript 送信。
-   SMTP / STARTTLS / SMTP 認証。
-   `MAIL_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
    の環境変数設定。

## v0.0.0

初期版。

-   計算機から REST API で PC 上の通知サーバーへ通知要求を送信。
-   メールアカウントや SMTP パスワードを計算機側へ置かない構成。
-   macOS Mail.app、Microsoft Outlook for Mac、SMTP に対応。
