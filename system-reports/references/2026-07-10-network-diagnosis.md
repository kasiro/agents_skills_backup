# ПОЛНЫЙ ОТЧЁТ ДИАГНОСТИКИ СЕТИ — 10.07.2026

## Система
- ОС: CachyOS Linux
- Ядро: 6.18.36-1-cachyos-lts
- Интерфейс: enp3s0 (Realtek r8169, RTL8168g, драйвер r8169)
- Роутер: RT-GPON-E400 (Ростелеком, GPON ONT)
- WiFi: отключён (wlan0 DOWN, NM: unavailable)
- Управление сетью: NetworkManager + systemd-resolved
- Docker: есть (docker0, br-c10d1982656c)

## Конфигурация до диагностики
- MTU: 1500 (стандарт)
- tcp_mtu_probing: 0 (ВЫКЛЮЧЕН — проблема)
- IP: 192.168.0.17/24 через DHCP
- Шлюз: 192.168.0.1
- DNS: systemd-resolved (127.0.0.53), выше 1.1.1.1, 8.8.8.8
- Firewall: не блокирует (OUTPUT ACCEPT)
- Bonding: отсутствует

---

## ПРОБЛЕМА №1 — КРИТИЧЕСКАЯ: Повреждённый Ethernet-кабель

### Симптомы
- Downshift 1Gbps → 100Mbps — 3 эпизода за сессию
- Ядро пишет: "Downshift occurred from negotiated speed 1Gbps to actual speed 100Mbps, check cabling!"
- 2 падения линка (Link is Down) с последующим переподключением
- TX dropped: 17-26, Retransmits TCP: 67 910
- Connections aborted due timeout: 114
- 100% loss ping до шлюза на момент ухудшения

### Доказательства (dmesg)
```
[   31.822176] Downshift occurred from negotiated speed 1Gbps to actual speed 100Mbps, check cabling!
[  116.441078] Downshift occurred from negotiated speed 1Gbps to actual speed 100Mbps, check cabling!
[ 2593.830111] Downshift occurred from negotiated speed 1Gbps to actual speed 100Mbps, check cabling!
```

### Причина
Физическое повреждение Ethernet-кабеля (Cat5e/Cat6):
- Перебит, пережат мебелью, окисление контактов RJ-45
- Или некачественный коннектор
- Или порт на роутере не держит гигабит

### Лечение — немедленное (стабилизация до замены кабеля)
```bash
# Зафиксировать 100Mbps чтобы линк не прыгал
doas ethtool -s enp3s0 speed 100 duplex full autoneg off
```

### Лечение — постоянное (после покупки нового кабеля)
```bash
# 1. Купить новый кабель Cat5e или Cat6
# 2. Подключить
# 3. Вернуть автосогласование:
doas ethtool -s enp3s0 autoneg on
# Ожидать: Speed: 1000Mbps, 0% loss, 0 dropped
```

---

## ПРОБЛЕМА №2 — ИСПРАВЛЕНА: tcp_mtu_probing=0

### Симптомы
- HTTPS сайты не открывались (таймаут соединения)
- HTTP (80 порт) тоже не работал
- DNS (TCP/53) — работал
- Ping 8.8.8.8 (64 байта) — 80% успеха, ~64ms
- Скорость ~68 KB/s при тесте curl

### Доказательство
- При MTU 1492: google.com заработал (TLS handshake успешен)
- При MTU 1400: ya.ru заработал (TLS 1.3 handshake)
- При MTU 1500: всё падает

### Причина
TCP не адаптировался к MTU пути. Провайдер использует PPPoE (MTU 1492), на интерфейсе 1500. Размер 1500 не проходит — фрагментация или отбрасывание без ICMP уведомления.

### Исправление (уже применено)
```bash
# Включение PMTU discovery (постоянно)
echo 'net.ipv4.tcp_mtu_probing=1' | doas tee /etc/sysctl.d/90-network-tune.conf
# Проверка:
doas sysctl net.ipv4.tcp_mtu_probing
# Должен быть: net.ipv4.tcp_mtu_probing = 1
```

---

## ПРОБЛЕМА №3 — Флаттер NetworkManager (CONNECTED_SITE ↔ CONNECTED_GLOBAL)

### Симптомы
- Интернет "то есть, то нет" — визуально моргает
- NetworkManager переключает состояние доступности
- Сайты то открываются, то нет

### Хронология флаттера
```
19:27:22 CONNECTED_GLOBAL  ✅
19:27:35 CONNECTED_SITE     ❓
19:27:39 CONNECTED_GLOBAL  ✅
19:39:22 CONNECTED_SITE     ❓
19:39:25 CONNECTED_GLOBAL  ✅
19:39:43 CONNECTED_SITE     ❓ (последнее)
```

### Причина
Прямое следствие проблемы №1 — на повреждённом кабеле битые пакеты, NM connectivity check не проходит, переключает состояние.

### Исправление (рекомендовано)
```bash
# Отключить проверку connectivity (чтобы NM не дёргался)
echo -e "\n[connectivity]\ninterval=0" | doas tee -a /etc/NetworkManager/NetworkManager.conf
doas systemctl restart NetworkManager
```

---

## ПРОБЛЕМА №4 — Флаттер DHCP (переподключения)

### Симптомы
- IP адрес меняется (.17 → .19) при переподключениях
- DHCP 2 полных цикла за 22 минуты

### Хронология DHCP
```
19:25:27 DHCP begin → no lease (после падения линка)
19:25:35 DHCP begin → canceled → no lease
19:25:36 DHCP begin
19:25:41 ✅ New lease 192.168.0.19
19:26:38 DHCP canceled → no lease
19:26:40 DHCP begin
19:26:42 ✅ New lease 192.168.0.19 (тот же IP)
```

### Причина
Прямое следствие проблемы №1 — линк падает, DHCP переполучает адрес.

### Исправление (рекомендовано — временное)
```bash
# Поставить статический IP вместо DHCP
doas nmcli connection modify "Проводное подключение 1" ipv4.method manual
doas nmcli connection modify "Проводное подключение 1" ipv4.address 192.168.0.19/24
doas nmcli connection modify "Проводное подключение 1" ipv4.gateway 192.168.0.1
doas nmcli connection modify "Проводное подключение 1" ipv4.dns "1.1.1.1 8.8.8.8"
doas nmcli connection down "Проводное подключение 1" && doas nmcli connection up "Проводное подключение 1"
```

### Возврат DHCP (после замены кабеля)
```bash
doas nmcli connection modify "Проводное подключение 1" ipv4.method auto
doas nmcli connection modify "Проводное подключение 1" ipv4.address ""
doas nmcli connection modify "Проводное подключение 1" ipv4.gateway ""
doas nmcli connection modify "Проводное подключение 1" ipv4.dns ""
doas nmcli connection down "Проводное подключение 1" && doas nmcli connection up "Проводное подключение 1"
```

---

## ДОПОЛНИТЕЛЬНЫЕ НАХОДКИ

### ASPM
- dmesg: "can't disable ASPM; OS doesn't have ASPM control"
- Известная проблема Realtek r8169 на новых ядрах
- Может вызывать микро-замирания на PCIe, но не является причиной downshift
- **Вердикт:** некритично

### MAC адрес
- Текущий: da:66:97:be:b8:7a (spoofed)
- Реальный производителя: bc:ee:7b:e2:c1:41
- Это нормально для NetworkManager (MAC randomization)

### Firewall
- INPUT: ACCEPT (чисто)
- FORWARD: DROP (Docker правила, норма)
- OUTPUT: ACCEPT (чисто)
- **Вердикт:** не блокирует ничего

---

## ИТОГОВЫЙ ПЛАН ДЕЙСТВИЙ

### Сделать СЕЙЧАС (в порядке приоритета):
1. Заменить кабель Ethernet на новый Cat5e/Cat6
2. После замены: `doas ethtool -s enp3s0 autoneg on` — вернуть автосогласование
3. Проверить: `doas ethtool enp3s0 | grep Speed` → 1000Mbps
4. Проверить: `ping -c 100 -i 0.1 192.168.0.1` → 0% loss

### Если кабель купить прямо сейчас нельзя:
1. `doas ethtool -s enp3s0 speed 100 duplex full autoneg off` — стабилизировать линк
2. `doas nmcli connection modify "Проводное подключение 1" ipv4.method manual ...` — статика
3. `echo -e "\n[connectivity]\ninterval=0" | doas tee -a /etc/NetworkManager/NetworkManager.conf` — отключить флаттер
4. `doas systemctl restart NetworkManager`

### Уже сделано:
- ✅ `tcp_mtu_probing=1` — включён постоянно
- ✅ MTU 1500 — стандарт (PMTU автоопределение)

---

## Файлы и артефакты
- `/etc/sysctl.d/90-network-tune.conf` — настройка tcp_mtu_probing
- `~/.agents/skills/system-reports/SKILL.md` — протокол диагностики
- `~/.agents/skills/system-reports/references/2026-07-10-network-diagnosis.md` — данный отчёт

---

## ДИАГНОСТИКА WiFi — 10.07.2026

### Исходное состояние (2.4 GHz, канал 9, авто)
- Сигнал: -48 dBm (отлично), Quality 62/70
- TX Bitrate: 144.4 Mb/s
- RX Bitrate: 6.5 Mb/s (аномально — интерференция на канале 9)
- Потери до шлюза: 60%
- Потери до 8.8.8.8: 40%
- Скорость: ~0.5 Mbps
- Соседних сетей на 2.4 GHz: 7

### Попытка 5 GHz
- Команда: nmcli connection modify "RT-GPON-E400" 802-11-wireless.band a
- Результат: роутер RT-GPON-E400 не вещает на 5 GHz (не поддерживает или отключено)

### После смены канала с 9 на 7
- RX Bitrate: 117.0 Mb/s (было 6.5 — в 18 раз лучше)
- TX Bitrate: 144.4 Mb/s
- Потери до шлюза: 40% (было 60%)
- Потери до 8.8.8.8: 15% (было 40%)
- Скорость: ~0.6 Mbps (упирается в провайдера)
- Пинг шлюз: avg 1.26 ms
- Пинг 8.8.8.8: avg 65.93 ms

### Итог по WiFi
- Канал починили (RX 117 Mb/s вместо 6.5)
- Скорость упёрлась в провайдера (~0.6 Mbps) — WiFi не виноват
- Рекомендация: вернуться на провод (даёт 100 Mbps даже с битым кабелем)

---

## РОУТЕР RT-GM2-9 — ДИАГНОСТИКА (10.07.2026)

### Информация из веб-панели
| Параметр | Значение |
|----------|----------|
| Модель | Iskratel RT-GM2-9 (SBB3012B0 HW:A3) |
| Прошивка | 1.6.1381 |
| CPU | 8%, 52°C |
| GPON RX | -15 dBm (норма) |
| WAN | ppp0.1 (PPPoE), IP 95.191.193.34 |
| Время uptime | 40 суток |
| Время WAN-сессии | 10 суток |
| WiFi 2.4 GHz | RT-GPON-E400 (вкл) |
| WiFi 5 GHz | RT-5GPON-E400 (вкл) |

### Таблица маршрутизации
- Default: 0.0.0.0/0 → 100.81.64.1 via ppp0.1 (PPPoE)
- Внутренние: 10.25.80.0/21, 10.143.x.x via nas2
- LAN: 192.168.0.0/24 via br2

### Проблемы
1. Connection tracking overflow (40 суток uptime)
2. PPPoE-сессия может «спать»
3. Веб-интерфейс работает с перебоями
4. CPU перегружается периодически

### Автоперезагрузка
- Встроенный планировщик: ❌ Нет
- SSH: ✅ через superadmin (rootkit-sys/RT-GM2-9)
- Crontab на роутере: ❌ не сохраняется (/var/ tmpfs)
- Рекомендация: cron на ПК + SSH или умная розетка

### Superadmin
```bash
git clone https://github.com/rootkit-sys/RT-GM2-9
python3 rt_gm2_9.py -L admin -P <пароль>
```

### WiFi-адаптер ПК
- TP-Link TL-WN823N v2/v3, чип RTL8192EU
- Single-band: 2.4 GHz only (5 GHz не поддерживается)
- Для 5 GHz: TP-Link Archer T3U (RTL8812BU)
