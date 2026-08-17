#!/usr/bin/env python3
"""Построить маршрут на Яндекс Картах от точки A до точки B в Firefox с чистым профилем"""

import sys
import asyncio
import argparse
from pathlib import Path

parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from _firefox_clean import open_firefox_clean


async def execute(context):
    slots = context.get("slots", {})
    route_from = slots.get("from", "")
    route_to = slots.get("to", "")

    if not route_from or not route_to:
        print(f"[Jarvis:ERROR] Missing route points: need 'from' and 'to'")
        return {"success": False, "error": "missing route points"}

    url = f"https://yandex.ru/maps/?rtext=Новосибирск, {route_from}~Новосибирск, {route_to}"
    print(f"[Jarvis:INFO] Building route: {route_from} → {route_to} in clean Firefox...")
    success = open_firefox_clean(url)
    print(f"[Jarvis:INFO] Route is ready")
    return {"success": success}


def main():
    parser = argparse.ArgumentParser(description="Построить маршрут на Яндекс Картах")
    parser.add_argument("from_addr", help="Откуда")
    parser.add_argument("to_addr", help="Куда")
    args = parser.parse_args()

    context = {"slots": {"from": args.from_addr, "to": args.to_addr}}
    result = asyncio.run(execute(context))
    return result["success"]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python3 open_route.py <откуда> <куда>")
        print("Пример: python3 open_route.py 'ул. Ленина, 1' 'ул. Пушкина, 10'")
        sys.exit(1)
    sys.exit(0 if main() else 1)
