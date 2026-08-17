---
name: system-reports
description: |-
  Полная системная диагностика Linux: сеть, Ethernet, Wi-Fi, DNS, память, диски, нагрузка, процессы, логи, dmesg, MTU/PMTU discovery, firewall.
  Сбор, анализ и сохранение структурированных отчётов с рекомендациями.
  Use proactively when: проблемы с сетью/интернетом, системные сбои, диагностика производительности,
  проверка конфигурации, поиск причин нестабильной работы.
  Всегда загружать при жалобах на скорость/доступность интернета, сетевых ошибках, системных лагах.

  Examples:
  - user: "интернет херово работает" → полная диагностика: ethtool, dmesg, ping, MTU, tcp_mtu_probing, firewall
  - user: "проверь систему" → диски, память, нагрузка, логи, dmesg
  - user: "диагностика сети" → L1-L7 полный цикл: кабель → линк → IP → DNS → TCP → HTTP/HTTPS
  - user: "почему тупит" → системная диагностика: cpu, ram, io, network, dmesg errors
  - user: "проверь интернет" → ping шлюз/внешние, DNS резолв, TCP порты, speedtest, MTU, tcp_mtu_probing
   - user: "сохрани отчёт" → структурированный отчёт в references/ + запись в memory blocks (knowledge) через memory_set/memory_replace
---
# system-reports

Скилл для системной диагностики и отчётов на Linux (CachyOS/Arch).

## Протокол диагностики сети (проверенный порядок)

При жалобах на интернет — строгий порядок проверки:

### L1 — Физический уровень
1. `ethtool <interface>` — Speed, Duplex, Link detected
2. `dmesg | grep -E '(r8169|enp3s0|downshift|Link is)'` — downshift, ошибки PHY
3. `ip -s link show <interface>` — errors, dropped

### L2 — Канальный уровень
4. `ip neigh show` — ARP таблица
5. `arping <gateway>` — L2 доступность шлюза

### L3 — Сетевой уровень
6. `ip addr show` — IP конфигурация
7. `ip route show` — маршрутизация
8. `ping -c 10 -s 64 <gateway>` — базовая связность
9. `ping -c 5 -M do -s 1472 <gateway>` — MTU проверка

### L4-L7 — Транспорт и приложения
10. `sysctl net.ipv4.tcp_mtu_probing` — PMTU discovery (должен быть 1!)
11. `ping -c 10 -s 64 8.8.8.8` — внешняя связность
12. `curl -v --connect-timeout 10 https://ya.ru` — HTTPS тест
13. `curl -v --connect-timeout 10 https://google.com` — HTTPS тест
14. `nc -zv 8.8.8.8 53 -w 5` — DNS TCP
15. `resolvectl status` — DNS конфигурация
16. `iptables -L -n -v` — firewall (должен быть ACCEPT на OUTPUT)

### Speed test
17. `curl -o /dev/null -s -w "Speed: %{speed_download} bytes/sec\n" --max-time 15 https://proof.ovh.net/files/10Mb.dat`

### Сохранение результатов
После завершения диагностики:
- Сохранить отчёт в `references/` с датой
- J.A.R.V.I.S. записывает итоги в memory blocks (блок knowledge, memory_set/memory_replace).

## Типовые проблемы и решения

| Симптом | Причина | Решение |
|---------|---------|---------|
| Downshift 1Gbps→100Mbps | Кабель повреждён | Заменить кабель Cat5e/Cat6 |
| HTTPS таймауты, DNS работает | tcp_mtu_probing=0 | sysctl -w net.ipv4.tcp_mtu_probing=1 |
| Link UP но 100% loss до шлюза | Кабель/порт роутера/ARP | Проверить ARP, переткнуть кабель, перезагрузить роутер |
| TX dropped > 0 | Перегрузка буфера (обычно при 100Mbps) | Решить проблему с кабелем |
| DNS не резолвит | Нет связи со шлюзом или DNS проблемы | Проверить resolvectl, /etc/resolv.conf |
