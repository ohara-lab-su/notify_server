# インストールと使用方法

`pip install notify-frame` でインストールします。同梱のサンプルスクリプトは `notify_server install` でカレントディレクトリへ配置します。既存ファイルを上書きする場合は `notify_server install --force` を指定します。

## 計算機側

```python
from notify import configure, notify
configure(server_url="http://your-pc:8000/notify", token="shared-token")
notify("Calculation started")
notify("Calculation finished", "Completed successfully")
```

`notify()` はデフォルトで失敗時に例外を伝播せず `False` を返します。例外を伝播させる場合は `strict=True` を指定します。環境変数 `NOTIFY_SERVER_URL` と `NOTIFY_TOKEN` も使用できます。

## PC側サーバー

```python
from notify.server import NotifyConfig, main
config = NotifyConfig(token="shared-token", backend="mail_client", mail_client="mail", mail_to="your_account@example.com")
main(config=config, host="0.0.0.0", port=8000)
```

macOS Mail.app、Microsoft Outlook（macOS/Windows）、SMTP（STARTTLS）に対応します。REST APIは `POST /notify` で、JSONの `title`、`body` と `X-Notify-Token` ヘッダーを使用します。HTTPサーバーをインターネットに直接公開しないでください。
