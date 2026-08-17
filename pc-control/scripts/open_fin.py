#!/usr/bin/env python3
"""Открыть финансы (ezbookkeeping)"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


def ensure_container_running(container_name):
    try:
        import docker
        client = docker.from_env()
        container = client.containers.get(container_name)
        if container.status == "running":
            print(f"Контейнер {container_name} уже запущен.")
        else:
            print(f"Контейнер {container_name} остановлен. Запускаем...")
            container.start()
            container.reload()
            print(f"Контейнер {container_name} запущен. Статус: {container.status}")
        return container
    except ImportError:
        print("⚠️ docker-py не установлен, пропускаю проверку контейнера")
        return None
    except Exception as e:
        print(f"❌ Ошибка с контейнером {container_name}: {e}")
        return None


async def execute(context):
    jarvis = init_jarvis(context)
    jarvis.audio.play_ok()

    ensure_container_running("ezbookkeeping")

    jarvis.environment.gtk_launch_background("WebApp-Финансы9154", 2)

    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
