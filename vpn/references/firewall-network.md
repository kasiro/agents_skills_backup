# Firewall и сеть

**IP в локальной сети:** 192.168.0.17 (интерфейс enp3s0)  
**Firewall:** iptables (nftables backend — Arch Linux)  
**Открытые порты:** 2113 (vless-online)  

Правило iptables:
```
sudo iptables -A INPUT -p tcp --dport 2113 -j ACCEPT
```

## ⚠️ Конфликт AmneziaVPN с iptables

**Проблема (из истории — 25.06.2026):** AmneziaVPN при включении split tunneling создаёт кастомные iptables цепочки `amnvpn.NUMBER.allowLAN`. При некорректной загрузке правил возникает ошибка:

```
iptables: Couldn't load target 'amnvpn.300.allowLAN': No such file or directory
```

**Последствия:**
- Блокируется localhost loopback (127.0.0.1)
- Локальные MCP сервера теряют связность
- OpenCode создаёт новые копии упавших MCP → процессная утечка (до 48 копий)
- Kernel hung tasks из-за перегрузки (rw-semaphore блокировки)

**Текущий статус (28.06.2026):**
- VPN отключён
- Проблема с amnvpn.allowLAN не наблюдается
- iptables чистые, политика INPUT ACCEPT
- Наши правила для порта 2113 совместимы

**Рекомендации:**
- Если включать AmneziaVPN с split tunneling — сначала проверить, что allowLAN цепочки созданы
- При возникновении ошибки — перезагрузить iptables: `sudo systemctl restart iptables.service`
- Или выключить split tunneling в настройках AmneziaVPN
