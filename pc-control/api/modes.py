"""
Modes API - Управление режимами: get_current, set_mode
"""
import sys
import asyncio
from typing import Optional
from pathlib import Path

from .state import State


class Modes:
    """
    Modes API для управления режимами Jarvis

    Режимы:
    - normal: обычный режим
    - kid: детский режим
    - dev: режим разработчика
    """

    VALID_MODES = ["normal", "kid", "dev"]

    def __init__(self, command_path: str = "", state: State = None):
        self.command_path = command_path
        self.state = state
        self._manager = None
        self._bus = None

    def _get_manager(self):
        if self._manager is None:
            try:
                from .mode_manager import ModesManager
                self._manager = ModesManager(self.state)
            except ImportError as e:
                print(f"[Jarvis:MODES] Failed to import ModesManager: {e}", file=sys.stderr)
                return None
        return self._manager

    def _get_bus(self):
        if self._bus is None:
            try:
                from .event_bus import get_bus
                self._bus = get_bus()
            except ImportError as e:
                print(f"[Jarvis:MODES] Failed to import EventBus: {e}", file=sys.stderr)
                return None
        return self._bus

    def get_current(self) -> str:
        manager = self._get_manager()
        if manager:
            return manager.get_current_mode()

        try:
            from .state import State
            state = State()
            mode = state.get("mode", "normal")
            return mode if mode in self.VALID_MODES else "normal"
        except Exception:
            return "normal"

    async def set_mode(self, new_mode: str) -> bool:
        if new_mode not in self.VALID_MODES:
            print(f"[Jarvis:MODES] Invalid mode: {new_mode}. Valid modes: {self.VALID_MODES}", file=sys.stderr)
            return False

        manager = self._get_manager()
        if manager:
            try:
                if asyncio.iscoroutinefunction(manager.set_mode):
                    success = await manager.set_mode(new_mode)
                else:
                    success = manager.set_mode(new_mode)

                if success:
                    print(f"[Jarvis:MODES] Mode set to: {new_mode}", file=sys.stderr)
                else:
                    print(f"[Jarvis:MODES] Failed to set mode: {new_mode}", file=sys.stderr)
                return success
            except Exception as e:
                print(f"[Jarvis:MODES] Error setting mode: {e}", file=sys.stderr)
                return False

        try:
            from .state import State
            state = State(self.command_path)
            state.set("mode", new_mode)
            print(f"[Jarvis:MODES] Mode set to: {new_mode} (fallback)", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[Jarvis:MODES] Fallback failed: {e}", file=sys.stderr)
            return False

    def is_kid_mode(self) -> bool:
        return self.get_current() == "kid"

    def is_dev_mode(self) -> bool:
        return self.get_current() == "dev"

    def is_normal_mode(self) -> bool:
        return self.get_current() == "normal"


# Глобальный экземпляр
modes = Modes()
