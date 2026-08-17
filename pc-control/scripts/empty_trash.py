#!/usr/bin/env python3
"""Очистить корзину"""
import subprocess
import os
import sys


def main():
    try:
        # Метод 1: dbus Nautilus
        subprocess.run([
            "dbus-send", "--session", "--dest=org.gnome.Nautilus",
            "--type=method_call", "/org/gnome/Nautilus/FileOperations",
            "org.gnome.Nautilus.FileOperations.EmptyTrash"
        ], check=False)

        # Метод 2: rm -rf
        trash_path = os.path.expanduser("~/.local/share/Trash")
        for folder in ["files", "info", "expunged"]:
            path = os.path.join(trash_path, folder)
            if os.path.exists(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    subprocess.run(["rm", "-rf", item_path], check=False)

        print("✅ Корзина очищена")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
