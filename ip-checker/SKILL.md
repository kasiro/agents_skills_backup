---
name: ip-checker
description: |-
  Определение внешнего и локального IP-адреса через несколько провайдеров (ifconfig.me, ipify.org, icanhazip.com, api.ipify.org). 
  Использовать когда нужно узнать IP адрес сервера, проверить NAT, или диагностировать сетевое подключение.
  
  Examples:
  - user: "узнай мой IP" → определить внешний IP через все провайдеры
  - user: "какой IP у сервера" → показать внешний и локальный IP
  - user: "проверь ip адрес" → показать внешний IP
  - user: "диагностика сети ip" → проверить IP через все сервисы с таймаутами
---
# IP Checker

Определение внешнего IP-адреса через несколько провайдеров.

## Быстро

```bash
python3 scripts/get_ip.py
```

## Скрипт get_ip.py

Файл `scripts/get_ip.py`:

```python
#!/usr/bin/env python3
"""Определение внешнего и локального IP-адреса."""

import subprocess
import urllib.request
import urllib.error
import socket
import sys


PROVIDERS = [
    ("ifconfig.me", "https://ifconfig.me/ip"),
    ("ipify.org", "https://api.ipify.org"),
    ("icanhazip.com", "https://icanhazip.com"),
    ("ip-api.com", "http://ip-api.com/ip"),
]


def get_local_ip() -> str:
    """Определить локальный IP."""
    try:
        hostname = socket.gethostname()
        local = socket.gethostbyname(hostname)
        return local
    except Exception as e:
        return f"ошибка: {e}"


def get_external_ips(timeout: int = 5) -> list:
    """Определить внешний IP через всех провайдеров."""
    results = []
    for name, url in PROVIDERS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                ip = resp.read().decode("utf-8").strip()
                results.append((name, ip, "✅"))
        except urllib.error.URLError as e:
            results.append((name, str(e.reason), "❌"))
        except Exception as e:
            results.append((name, str(e), "❌"))
    return results


def print_results(local: str, external: list):
    """Красивый вывод."""
    print("🌐 IP Checker")
    print("=" * 40)
    print(f"🏠 Локальный: {local}")
    print()
    print("📡 Внешние IP:")
    for name, ip, status in external:
        print(f"  {status} {name:20s} → {ip}")
    print("=" * 40)


if __name__ == "__main__":
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    local = get_local_ip()
    external = get_external_ips(timeout)
    print_results(local, external)
    
    # Вывод для скриптов (машиночитаемый)
    # Первый успешный IP как "основной"
    for name, ip, status in external:
        if status == "✅":
            print(f"\nIP={ip}")
            break
