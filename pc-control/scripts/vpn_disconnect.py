#!/usr/bin/env python3
"""Отключить VPN (AmneziaVPN)"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis
from api.vpn import VPNController


async def execute(context):
    """Отключить VPN"""
    jarvis = init_jarvis(context)

    VPNController(cleanup=True)

    jarvis.log("info", "vpn closed")
    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
