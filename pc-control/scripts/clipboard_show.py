#!/usr/bin/env python3
"""Показать содержимое буфера обмена"""
import subprocess
import sys


def main():
    tools = [
        ["wl-paste"],
        ["xclip", "-selection", "clipboard", "-o"],
        ["xsel", "--clipboard", "--output"]
    ]

    for tool in tools:
        try:
            result = subprocess.run(tool, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                print(f"📋 Буфер обмена: {result.stdout.strip()}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    print("📋 Буфер обмена пуст или не поддерживается")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
