#!/usr/bin/env python3
"""Смена раскладки клавиатуры"""
import subprocess
import sys


def main():
    try:
        # Метод 1: xdotool
        result = subprocess.run(["xdotool", "key", "Super+Space"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Раскладка переключена")
            return True
    except FileNotFoundError:
        pass

    try:
        # Метод 2: setxkbmap переключение
        result = subprocess.run(["setxkbmap", "-query"], capture_output=True, text=True, timeout=5)
        if "us" in result.stdout:
            subprocess.run(["setxkbmap", "ru"], check=True)
        else:
            subprocess.run(["setxkbmap", "us"], check=True)
        print("✅ Раскладка переключена")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
