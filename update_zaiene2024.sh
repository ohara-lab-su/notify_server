#!/usr/bin/env bash
#
#
#server="zaiene-hpcs2024"
server="zaiene-hpcs2024-bridge2023"
dst_dir="zaiene_dev/notify_server/"

# ローカルからリモートへ同期
# rsync -avz -e ssh --delete ./ "$server:~/$dst_dir"
rsync -avz -e ssh --checksum  --delete ./ "$server:~/$dst_dir"

# 転送先で pip install . を実行
ssh "$server" "cd ~/$dst_dir && ~/.pyenv/shims/pip install ."
