#!/usr/bin/env python3
"""Подключить VPN (AmneziaVPN)"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis
from api.vpn import VPNController


async def execute(context):
    """Запустить VPN"""
    jarvis = init_jarvis(context)

    vpn = VPNController(server_index=1, cleanup=False)
    if not vpn.is_connected():
        vpn.connect()

    jarvis.environment.minimize_window("AmneziaVPN")

    jarvis.log("info", "vpn is ready")
    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
