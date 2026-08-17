---
name: router-diagnostics
description: |-
  Диагностика GPON-роутера Iskratel RT-GM2-9 (Ростелеком) через веб-интерфейс.
  Доступ к логам, GPON статусу, PPPoE, syslog. Выявление причин сбоев: PON линк,
  dnsmasq crash, переполнение conntrack, температура, оптическая мощность.
  Использовать когда интернет пропадает, роутер перезагружается, нужна диагностика.
  
  Examples:
  - user: "интернет пропадает" → проверить логи st_log_tl.htm, GPON статус
  - user: "роутер перезагружается" → PON link state, dnsmasq crash, температура
  - user: "проверь роутер" → deviceinfo, waninfo, syslog за сегодня
  - user: "посмотри логи роутера" → st_log_tl.htm через Basic Auth
  - user: "диагностика GPON" → оптическая мощность, PON статус O1-O5
---
# Диагностика роутера Iskratel RT-GM2-9

## Доступ к веб-интерфейсу

**Адрес:** http://192.168.0.1
**Логин:** admin / пароль из наклейки на роутере

### Basic Auth
```bash
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_deviceinfo_tl.htm
```

## Диагностические страницы

### 1. Информация об устройстве (GPON статус)
```
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_deviceinfo_tl.htm
```
**Ключевые поля:**
- `m_ontTemp` — температура ONT (норма < 55°C)
- `m_deivice_optical_pwr` — оптическая мощность RX (норма -8 до -27 dBm)
- `m_ponStatus` — статус PON (O5 = Operational = норма)
- `M_iUpTime` — uptime роутера
- `swVersion` — версия прошивки

### 2. Системный лог (syslog) — САМАЯ ВАЖНАЯ СТРАНИЦА
```
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_log_tl.htm
```
Логи хранятся в JavaScript-массиве `dataLists[]`. Извлечение:
```bash
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_log_tl.htm | \
  python3 -c "
import sys, re
html = sys.stdin.read()
matches = re.findall(r'dataLists\[\d+\]=\"([^\"]*)\"', html)
for m in matches:
    print(m)
" | tail -50
```

**Критические строки в логах:**
- `PON:Link state change to down` — GPON потерял синхронизацию!
- `dnsmasq crash restart` — DNS/DHCP сервер упал
- `PAP authentication succeeded` — PPPoE переподключился
- `LAN1 is down` — порт Ethernet отвалился
- `admin login success` — кто-то заходил в админку

### 3. WAN информация
```
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_waninfo_tl.htm
```
**Ключевые поля:**
- PON Status (O5 = норма, O1-O4 = активация)
- PPPoE session status
- IP адрес, шлюз, DNS
- Uptime PPPoE сессии

### 4. Таблица маршрутизации
```
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_route_tl.htm
```

### 5. ARP таблица
```
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_arp_tl.htm
```

### 6. Network Setup (карта сети)
```
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_network_setup_tl.htm
```

### 7. Конфигурация (только superadmin)
```bash
# 1. Получить sessionKey
KEY=$(curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/advanced/conSession.htm?id=666 | grep -oP '\d+')

# 2. Скачать конфиг (зашифрован AES)
curl -s "http://192.168.0.1/config_old_tl.xgi?sessionKey=$KEY" -o config.bin
```

## Получение superadmin

```bash
git clone https://github.com/rootkit-sys/RT-GM2-9
cd RT-GM2-9
pip3 install PyCryptodome requests paramiko
python3 rt_gm2_9.py -L admin -P <ПАРОЛЬ_С_НАКЛЕЙКИ>
# Пароль запишется в superadmin.txt
python3 rt_gm2_9.py -L admin -P <ПАРОЛЬ> -S -T  # включить SSH + отключить TR-069
```

## Таблица состояний PON

| Состояние | Описание | Норма? |
|-----------|----------|--------|
| O1 | Disabled | ❌ Проблема |
| O2 | Standby | ⏳ Активация |
| O3 | Serial ID | ⏳ Активация |
| O4 | Ranging | ⏳ Активация |
| **O5** | **Operational** | ✅ Работает |
| O6 | Interrupted LOS | ❌ Потеря сигнала |
| O7 | Emergency Stop | ❌ Авария |

## Типовые проблемы и диагнозы

### 🔴 PON линк падает (O5 → O1)
**В логах:** `PON:Link state change to down`
**Причины:**
1. Грязный оптический коннектор — протереть спиртовой салфеткой
2. Перегиб/повреждение оптического патч-корда
3. Проблема на OLT (сторона провайдера)
4. Деградация GPON-модуля роутера
**Действие:** Проверить RX мощность (-15 dBm норма), позвонить Ростелекому

### 🔴 dnsmasq crash restart
**В логах:** `APPMGR:[dnsmasq crash restart:N]`
**Причина:** Краш DNS/DHCP сервера роутера
**Действие:** Если крашится 1 раз при загрузке — норма. Если крашится постоянно — проблема прошивки.

### 🔴 Роутер перегружается каждые 30-120 минут
**Причина:** Аппаратная проблема (GPON модуль, блок питания, нагрев)
**Диагностика:**
```bash
# Проверить uptime роутера
m_iUpTime
# Проверить температуру
m_ontTemp
# Проверить кол-во PON сбоев
grep -c "PON:Link state change to down" logs
```

### 🟡 Downshift Ethernet 1Gbps → 100Mbps
**В dmesg:** `Downshift occurred from negotiated speed 1Gbps to actual speed 100Mbps, check cabling!`
**Причина:** Повреждённый Ethernet-кабель между ПК и роутером
**Решение:** Заменить патч-корд на Cat5e/Cat6

### 🟡 Температура ONT > 55°C
**Причина:** Плохая вентиляция
**Решение:** Обеспечить циркуляцию воздуха, поставить вертикально

## Полный протокол диагностики

```bash
# 1. Информация об устройстве
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_deviceinfo_tl.htm

# 2. WAN статус
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_waninfo_tl.htm

# 3. Логи (syslog)
curl -s -u "admin:ПАРОЛЬ" http://192.168.0.1/status/st_log_tl.htm | \
  python3 -c "
import sys, re
html = sys.stdin.read()
matches = re.findall(r'dataLists\[\d+\]=\"([^\"]*)\"', html)
for m in matches:
    print(m)
" | grep -i -E '(pon|dnsmasq|ppp|pap|link|down|up|crash|error|fail|admin|dhcp)' | tail -30

# 4. Проверка Ethernet адаптера ПК
dmesg | grep -i -E '(enp3s0|r8169|downshift|error|fail|timeout|link)'

# 5. Ping внешние хосты
ping -c 5 -s 64 8.8.8.8
curl -o /dev/null -s -w "HTTP: %{http_code}, Time: %{time_total}s\n" --connect-timeout 10 https://ya.ru
```

## Автоперезагрузка (cron на ПК)

```bash
# Получить superadmin → включить SSH
# Добавить в crontab:
30 4 */3 * * sshpass -p 'PASS' ssh -o StrictHostKeyChecking=no superadmin@192.168.0.1 'reboot'
```

Или умная розетка Tuya/Sonoff (~500₽) с расписанием.

## Сохранение результатов

После диагностики:
1. Сохранить отчёт в memory, используя скилл how_use_memory:
   - Загрузить skill("how_use_memory")
   - Записать итоги в memory blocks (knowledge/lessons) через memory_set/memory_replace
2. Сохранить урок с тегами: router, GPON, RT-GM2-9, Ростелеком (используя скилл how_use_memory)
3. Если найдена новая проблема — обновить этот скилл
