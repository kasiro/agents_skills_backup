"""
System API - Взаимодействие с ОС: notify, open, exec, clipboard, env, platform
"""
import os
import sys
import subprocess
import platform
from typing import Optional, Dict, Any, List


class System:
    """
    System API для взаимодействия с операционной системой
    """

    def __init__(self):
        self._platform = self._detect_platform()

    def _detect_platform(self) -> str:
        """Определить платформу"""
        if sys.platform.startswith("win"):
            return "windows"
        elif sys.platform.startswith("darwin"):
            return "macos"
        elif sys.platform.startswith("linux"):
            return "linux"
        else:
            return "unknown"

    @property
    def platform(self) -> str:
        """Текущая платформа"""
        return self._platform

    async def open(self, target: str) -> bool:
        """
        Открыть URL или файл в приложении по умолчанию (АСИНХРОННО, не блокирует)

        Args:
            target: URL или путь к файлу

        Returns:
            True если успешно
        """
        import asyncio

        try:
            if self._platform == "windows":
                proc = await asyncio.create_subprocess_exec(
                    "cmd", "/C", "start", "", target,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                    start_new_session=True
                )
            elif self._platform == "macos":
                proc = await asyncio.create_subprocess_exec(
                    "open", target,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                    start_new_session=True
                )
            else:  # linux
                proc = await asyncio.create_subprocess_exec(
                    "xdg-open", target,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                    start_new_session=True
                )

            if proc.stdin:
                proc.stdin.close()

            print(f"[Jarvis:SYSTEM] Opened: {target}", file=sys.stderr)
            return True

        except (OSError, subprocess.SubprocessError) as e:
            print(f"[Jarvis:SYSTEM] Failed to open {target}: {e}", file=sys.stderr)
            return False

    def exec(self, cmd: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Выполнить системную команду (с ожиданием завершения)

        Args:
            cmd: Команда
            args: Аргументы команды

        Returns:
            Dict с ключами: success, code, stdout, stderr
        """
        try:
            if args:
                full_cmd = [cmd] + args
            else:
                if self._platform == "windows":
                    full_cmd = ["cmd", "/C", cmd]
                else:
                    full_cmd = ["bash", "-c", cmd]

            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "code": -1,
                "stdout": "",
                "stderr": "Command timed out"
            }
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            return {
                "success": False,
                "code": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def exec_background(self, cmd: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Выполнить системную команду в фоновом режиме (без ожидания)

        Args:
            cmd: Команда
            args: Аргументы команды

        Returns:
            Dict с ключами: success, pid (process id)
        """
        try:
            if args:
                full_cmd = [cmd] + args
            else:
                if self._platform == "windows":
                    full_cmd = ["cmd", "/C", cmd]
                else:
                    full_cmd = ["bash", "-c", cmd]

            proc = subprocess.Popen(
                full_cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            return {
                "success": True,
                "pid": proc.pid
            }

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            return {
                "success": False,
                "pid": None,
                "error": str(e)
            }

    def notify(self, title: str, message: str) -> bool:
        """
        Показать системное уведомление

        Args:
            title: Заголовок
            message: Сообщение

        Returns:
            True если успешно
        """
        try:
            if self._platform == "windows":
                script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastText02">
                            <text id="1">{title}</text>
                            <text id="2">{message}</text>
                        </binding>
                    </visual>
                </toast>
        "@

                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Jarvis").Show($toast)
                """
                subprocess.run(
                    ["powershell", "-Command", script],
                    capture_output=True,
                    timeout=5
                )
            elif self._platform == "macos":
                applescript = f'display notification "{message}" with title "{title}"'
                subprocess.run(
                    ["osascript", "-e", applescript],
                    capture_output=True,
                    timeout=5
                )
            else:  # linux
                subprocess.run(
                    ["notify-send", title, message],
                    capture_output=True,
                    timeout=5
                )

            return True

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"[Jarvis:SYSTEM] Failed to show notification: {e}", file=sys.stderr)
            return False

    class Clipboard:
        """Clipboard подмодуль"""

        def __init__(self, platform: str):
            self._platform = platform

        def get(self) -> Optional[str]:
            """Получить содержимое буфера обмена"""
            try:
                if self._platform == "windows":
                    result = subprocess.run(
                        ["powershell", "-Command", "Get-Clipboard"],
                        capture_output=True,
                        text=True
                    )
                    return result.stdout.strip()
                elif self._platform == "macos":
                    result = subprocess.run(
                        ["pbpaste"],
                        capture_output=True,
                        text=True
                    )
                    return result.stdout
                else:  # linux
                    try:
                        result = subprocess.run(
                            ["xclip", "-selection", "clipboard", "-o"],
                            capture_output=True,
                            text=True
                        )
                        return result.stdout
                    except FileNotFoundError:
                        result = subprocess.run(
                            ["xsel", "--clipboard", "--output"],
                            capture_output=True,
                            text=True
                        )
                        return result.stdout
            except (subprocess.SubprocessError, FileNotFoundError):
                return None

        def set(self, text: str) -> bool:
            """Установить содержимое буфера обмена"""
            try:
                if self._platform == "windows":
                    script = f"Set-Clipboard -Value '{text.replace("'", "''")}'"
                    subprocess.run(
                        ["powershell", "-Command", script],
                        capture_output=True
                    )
                elif self._platform == "macos":
                    proc = subprocess.Popen(
                        ["pbcopy"],
                        stdin=subprocess.PIPE,
                        text=True
                    )
                    proc.communicate(text)
                else:  # linux
                    try:
                        proc = subprocess.Popen(
                            ["xclip", "-selection", "clipboard"],
                            stdin=subprocess.PIPE,
                            text=True
                        )
                        proc.communicate(text)
                    except FileNotFoundError:
                        proc = subprocess.Popen(
                            ["xsel", "--clipboard", "--input"],
                            stdin=subprocess.PIPE,
                            text=True
                        )
                        proc.communicate(text)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                return False

    @property
    def clipboard(self) -> Clipboard:
        """Буфер обмена"""
        return self.Clipboard(self._platform)

    def env(self, name: str) -> Optional[str]:
        """
        Получить переменную окружения

        Args:
            name: Имя переменной

        Returns:
            Значение или None
        """
        return os.environ.get(name)


# Глобальный экземпляр
system = System()
