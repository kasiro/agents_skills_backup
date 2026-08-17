"""
Environment API - Управление окружением и окнами

Интеграция с wayland.py и wm_manager.py
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class Environment:
    """
    Environment API для управления окружением и окнами
    """

    def __init__(self):
        self._wayland = None
        self._wm = None
        self._app_manager = None

    def _init_wayland(self):
        """Ленивая инициализация WaylandController"""
        if self._wayland is None:
            try:
                from .wayland import WaylandController
                self._wayland = WaylandController()
            except ImportError as e:
                print(f"[Jarvis:ENV] Failed to import WaylandController: {e}", file=sys.stderr)
                return None
        return self._wayland

    def _init_window_manager(self):
        """Ленивая инициализация WindowManager"""
        if self._wm is None:
            try:
                from .wm_manager import WindowManager
                self._wm = WindowManager()
            except ImportError as e:
                print(f"[Jarvis:ENV] Failed to import WindowManager: {e}", file=sys.stderr)
                return None
        return self._wm

    def _init_app_manager(self):
        """Ленивая инициализация AppManager"""
        if self._app_manager is None:
            try:
                from .wm_manager import AppManager
                self._app_manager = AppManager()
            except ImportError as e:
                print(f"[Jarvis:ENV] Failed to import AppManager: {e}", file=sys.stderr)
                return None
        return self._app_manager

    # ===== Wayland Control =====

    def press_tab(self, count: int = 1, delay=0.1):
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.press_tab(count, delay)
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error pressing tab count({count}): {e}", file=sys.stderr)
            return False

    def type_text(self, text: str):
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.type_text(text)
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error typing text({text}): {e}", file=sys.stderr)
            return False

    def type_text_english(self, text: str, char_delay_ms=50, hold_delay_ms=30):
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.type_text_english(text, char_delay_ms=char_delay_ms, hold_delay_ms=hold_delay_ms)
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error typing text({text}): {e}", file=sys.stderr)
            return False

    def press_enter(self):
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.press_enter()
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error pressing enter: {e}", file=sys.stderr)
            return False

    def press_number(self, number: int):
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.press_number(number)
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error pressing number({number}): {e}", file=sys.stderr)
            return False

    def press_space(self):
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.press_space()
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error pressing space: {e}", file=sys.stderr)
            return False

    def press_super_number(self, number: int) -> bool:
        wayland = self._init_wayland()
        if not wayland:
            return False
        try:
            wayland.press_super_number(number)
            return True
        except Exception as e:
            print(f"[Jarvis:ENV] Error pressing Super+{number}: {e}", file=sys.stderr)
            return False

    # ===== Window Management =====

    def get_windows(self) -> List[Dict]:
        wm = self._init_window_manager()
        if not wm:
            return []
        return wm.get_windows()

    def minimize_all_windows(self) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm._minimize_all_manually()

    def minimize_window(self, wm_class: str) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm._minimize_window(wm_class)

    def maximize_window(self, wm_class: str) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm._maximize_window(wm_class)

    def focus_window(self, wm_class: str) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm._focus_window(wm_class)

    def maximize_all_windows(self) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm._maximize_all_manually()

    def is_app_running(self, wm_class: str) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm.is_running(wm_class)

    def move_window_to_workspace(self, window_id: int, workspace: int) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm.move_to_workspace(window_id, workspace)

    def move_to_workspace_wmclass(self, wmclass: str, workspace: int) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm.move_to_workspace_wmclass(wmclass, workspace)

    def wait_for_new_window_wmclass(self, wmclass: str, timeout: float = 10) -> bool:
        wm = self._init_window_manager()
        if not wm:
            return False
        return wm.wait_for_new_window_wmclass(wmclass, timeout)

    # ===== Application Launching =====

    def gtk_launch_app(self, app_name: str, workspace: int = 1):
        app_mgr = self._init_app_manager()
        if not app_mgr:
            return "❌ AppManager не доступен"
        return app_mgr.launcher.gtk_launch(app_name, workspace)

    def gtk_launch_background(self, app_name: str, workspace: int = 1):
        app_mgr = self._init_app_manager()
        if not app_mgr:
            return "❌ AppManager не доступен"
        return app_mgr.launcher.gtk_launch_background(app_name, workspace)

    def launch_app(self, app_name: str, workspace: int = 1) -> str:
        app_mgr = self._init_app_manager()
        if not app_mgr:
            return "❌ AppManager не доступен"
        return app_mgr.launcher.launch(app_name, workspace)

    def launch_or_move_app(self, app_name: str, wm_class: str, workspace: int):
        app_mgr = self._init_app_manager()
        if not app_mgr:
            return False
        app_mgr.launch_or_move(app_name, wm_class, workspace)
        return True

    def launch_or_move_app_background(self, app_name: str, wm_class: str, workspace: int):
        app_mgr = self._init_app_manager()
        if not app_mgr:
            return False
        app_mgr.launch_or_move_background(app_name, wm_class, workspace)
        return True

    # ===== Workspace Control =====

    def switch_to_workspace(self, number: int) -> bool:
        return self.press_super_number(number)


# Глобальный экземпляр
environment = Environment()
