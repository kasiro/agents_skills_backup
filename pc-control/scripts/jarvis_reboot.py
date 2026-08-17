#!/usr/bin/env python3
"""Перезагрузить Jarvis"""

import sys
import asyncio
from subprocess import CalledProcessError, check_output, run
from time import sleep


def get_pid_via_pgrep(process_name):
    try:
        output = check_output(["pgrep", process_name], text=True).strip()
        if "\n" in output:
            return [int(pid) for pid in output.split("\n") if pid]
        else:
            if output:
                return output
            return []
    except CalledProcessError:
        return []


async def execute(context):
    """Ребут Jarvis"""
    app_pid = get_pid_via_pgrep("jarvis-app")
    sleep(1.5)
    run(["/home/kasiro/Документы/jarvis/post_build.sh"])
    sleep(1.5)
    run(["/home/kasiro/Документы/jarvis/jarvis.sh"])
    sleep(1.5)
    if app_pid:
        run(["kill", "-9", str(app_pid)])
    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
