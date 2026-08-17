import os
import sys
from pathlib import Path
from subprocess import run
from time import sleep

# pydotool imports
pydotool = None
KEY_LEFTMETA = KEY_V = KEY_LEFTCTRL = KEY_SPACE = KEY_0 = KEY_1 = KEY_2 = KEY_3 = (
    KEY_4
) = KEY_L = KEY_TAB = KEY_ENTER = None

try:
    import pydotool
    from pydotool import (
        KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_ENTER, KEY_L, KEY_LEFTCTRL,
        KEY_LEFTMETA, KEY_SPACE, KEY_TAB, KEY_V,
    )
except ImportError:
    try:
        venv_path = Path("/home/kasiro/Документы/jarvis/.venv") / "lib"
        if venv_path.exists():
            for site_packages in venv_path.glob("*/site-packages"):
                sp_str = str(site_packages)
                if sp_str not in sys.path:
                    sys.path.append(sp_str)
                break

        import importlib
        pydotool = importlib.import_module("pydotool")
        KEY_LEFTMETA = getattr(pydotool, "KEY_LEFTMETA", None)
        KEY_0 = getattr(pydotool, "KEY_0", None)
        KEY_1 = getattr(pydotool, "KEY_1", None)
        KEY_2 = getattr(pydotool, "KEY_2", None)
        KEY_3 = getattr(pydotool, "KEY_3", None)
        KEY_4 = getattr(pydotool, "KEY_4", None)
        KEY_L = getattr(pydotool, "KEY_L", None)
        KEY_TAB = getattr(pydotool, "KEY_TAB", None)
        KEY_ENTER = getattr(pydotool, "KEY_ENTER", None)
        KEY_SPACE = getattr(pydotool, "KEY_SPACE", None)
        KEY_LEFTCTRL = getattr(pydotool, "KEY_LEFTCTRL", None)
        KEY_V = getattr(pydotool, "KEY_V", None)
    except ImportError:
        pass


class WaylandController:
    def __init__(self):
        self.pydotool = pydotool
        if pydotool:
            os.environ["YDOTOOL_SOCKET"] = "/run/user/1000/.ydotool_socket"
            pydotool.init()
        self.num_keys = {0: KEY_0, 1: KEY_1, 2: KEY_2, 3: KEY_3, 4: KEY_4}

    def press_enter(self):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        self.pydotool.key_combination([KEY_ENTER])

    def type_text(self, text: str):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        run(["wl-copy", text])
        self.pydotool.key_combination([KEY_LEFTCTRL, KEY_V])

    def type_text_english(self, text: str, char_delay_ms=50, hold_delay_ms=30):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        self.pydotool.type_string(text, each_char_delay_ms=char_delay_ms, hold_delay_ms=hold_delay_ms)

    def press_tab(self, count: int = 1, delay=0.1):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        if count > 1:
            for i in range(count):
                self.pydotool.key_combination([KEY_TAB])
                sleep(delay)
        else:
            self.pydotool.key_combination([KEY_TAB])

    def press_space(self):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        self.pydotool.key_combination([KEY_SPACE])

    def press_number(self, number: int):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        if number not in self.num_keys:
            raise ValueError(f"Неверная цифра: {number}. Допустимо от 0 до 4.")
        self.pydotool.key_combination([self.num_keys[number]])

    def press_super_number(self, number: int):
        if not self.pydotool:
            raise RuntimeError("pydotool не установлен")
        if number not in self.num_keys:
            raise ValueError(f"Неверная цифра: {number}. Допустимо от 0 до 4.")
        self.pydotool.key_combination([KEY_LEFTMETA, self.num_keys[number]])
