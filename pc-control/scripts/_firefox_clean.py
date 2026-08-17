#!/usr/bin/env python3
"""Запуск Firefox с чистым (нулевым) профилем"""
import subprocess
import tempfile
import os
import sys

FIREFOX_PROFILE_DIR = os.path.expanduser("~/.cache/pc-control-firefox-profile")


def open_firefox_clean(url: str) -> bool:
    """
    Открыть URL в Firefox с чистым изолированным профилем.
    Профиль создаётся один раз и переиспользуется.
    """
    os.makedirs(FIREFOX_PROFILE_DIR, exist_ok=True)
    
    try:
        subprocess.Popen([
            "firefox",
            "--profile", FIREFOX_PROFILE_DIR,
            "--no-remote",
            "--new-instance",
            url
        ], stdin=subprocess.DEVNULL,
           stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL,
           start_new_session=True)
        return True
    except FileNotFoundError:
        print("❌ Firefox не найден. Установите: doas pacman -S firefox", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска Firefox: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 _firefox_clean.py <url>")
        sys.exit(1)
    sys.exit(0 if open_firefox_clean(sys.argv[1]) else 1)
