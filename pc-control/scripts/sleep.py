#!/usr/bin/env python3
"""Спящий режим"""
import subprocess
import sys


def main():
    try:
        subprocess.run(["systemctl", "suspend"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
