#!/usr/bin/env bash

# notify.sh
#
# 計算コマンドの終了状態に応じて notify_client.py を呼び出す簡易ラッパー。
# メールアカウントやパスワードはここには書かない。
# NOTIFY_SERVER_URL と NOTIFY_TOKEN は環境変数で与える。

set -e

if ./run_calc.sh; then
    python3 notify_client.py "OK" "Calculation finished successfully."
else
    python3 notify_client.py "FAILED" "Calculation failed."
    exit 1
fi
