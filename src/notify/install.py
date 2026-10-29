"""インストール済みの共有データからサンプルスクリプトを配置する。"""
import argparse
import shutil
import sys
from pathlib import Path

SCRIPTS = ("notify.sh", "notify_example.py", "server_example.py")


def main() -> None:
    parser = argparse.ArgumentParser(prog="notify_server")
    parser.add_argument("command", choices=("install",))
    parser.add_argument("--force", action="store_true", help="既存ファイルを上書きする")
    args = parser.parse_args()

    # setuptools data-files はインストール環境の sys.prefix/share 以下に配置される。
    source_dir = Path(sys.prefix) / "share" / "notify-frame" / "scripts"
    missing = [name for name in SCRIPTS if not (source_dir / name).is_file()]
    if missing:
        parser.error(f"インストール済みスクリプトが見つかりません: {source_dir} ({', '.join(missing)})")

    for name in SCRIPTS:
        target = Path.cwd() / name
        if target.exists() and not args.force:
            print(f"Skipped (already exists): {target}")
            continue
        shutil.copyfile(source_dir / name, target)
        if name.endswith(".sh"):
            target.chmod(target.stat().st_mode | 0o111)
        print(f"Installed: {target}")
