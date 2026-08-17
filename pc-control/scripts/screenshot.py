#!/usr/bin/env python3
"""Сделать скриншот экрана"""
import subprocess
import os
from datetime import datetime
import sys


def main():
    screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(screenshot_dir, filename)

    tools = [
        ["gnome-screenshot", "-f", filepath],
        ["flameshot", "gui", "-p", screenshot_dir],
        ["grim", filepath]
    ]

    for tool in tools:
        try:
            result = subprocess.run(tool, capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Скриншот сохранён: {filepath}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    print("❌ Не найдена утилита для скриншотов (gnome-screenshot, flameshot, grim)", file=sys.stderr)
    return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
