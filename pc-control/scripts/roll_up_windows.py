#!/usr/bin/env python3
"""Свернуть все окна (Show Desktop)"""
import subprocess
import sys


def main():
    try:
        # Метод 1: GNOME Show Desktop через dbus
        subprocess.run([
            "dbus-send", "--session", "--dest=org.gnome.Shell",
            "--type=method_call", "/org/gnome/Shell",
            "org.gnome.Shell.Eval",
            "string:Main.wm.actionShowDesktop()"
        ], check=False)

        # Метод 2: xdotool fallback
        subprocess.run(["xdotool", "key", "super+d"], check=False)

        print("✅ Все окна свёрнуты")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
