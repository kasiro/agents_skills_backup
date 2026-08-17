---
name: zen-monitor
description: |-
  Мониторинг доступности и пиковых часов нагрузки OpenCode Zen Free API.
  Проверка через эндпоинты /zen/v1/models и /zen/v1/chat/completions.
  Сохранение в SQLite, JSON-лог, отчёты по часам/дням, детали ошибок.
  Настраиваемые модели, cron-мониторинг.
  
  Use proactively when: пользователь спрашивает о нагрузке Zen API, пиковых часах,
  доступности моделей, хочет проверить ошибки Zen, посмотреть статистику.
  
  Examples:
  - user: "как нагрузка на Zen?" → запустить отчёт за последние 12 часов
  - user: "какие ошибки были в 21:00?" → --time 21:00 --errors
  - user: "статистика по deepseek за сегодня" → --model deepseek --report --by-hour
  - user: "пиковые часы" → --report --by-hour
  - user: "добавь big-pickle в мониторинг" → -a big-pickle
---
# Zen Monitor — скрипт мониторинга Zen API

## Расположение

```
~/zen-monitor/
├── zen_monitor.py       # Основной скрипт (1000+ строк)
├── zen_data.db          # SQLite с историей проверок
├── zen_monitor.json     # JSON-лог (через --log)
└── README.md
```

## Быстрый старт

```bash
cd ~/zen-monitor

# Однократная проверка
python3 ./zen_monitor.py

# JSON (для автоматизации)
python3 ./zen_monitor.py --json

# Отчёты
python3 ./zen_monitor.py --report --hours 12    # за 12 часов
python3 ./zen_monitor.py --report --by-hour --hours 12    # по часам (12ч)
python3 ./zen_monitor.py --report --date 2026-07-02  # за дату
python3 ./zen_monitor.py --report --by-hour --hours 48

# Детали ошибок
python3 ./zen_monitor.py --errors --hours 12       # ошибки за 12 часов
python3 ./zen_monitor.py --time 21:00 --errors        # ошибки за час
python3 ./zen_monitor.py --time 21:00 --model deepseek --errors
python3 ./zen_monitor.py --time 21:00 --errors --json

# Настройка моделей
python3 ./zen_monitor.py --models deepseek,mimo,big-pickle
python3 ./zen_monitor.py -a big-pickle                # добавить на 1 запуск
export ZEN_MODELS="deepseek,mimo"
python3 ./zen_monitor.py --model deepseek              # фильтр отчёта

# Логирование
python3 ./zen_monitor.py --log   # дополняет валидный JSON-массив
```

## Формат таблицы --by-hour

```
            Hour   big-pickle     deepseek         mimo
                   err      n   err      n   err      n
───────────────────────────────────────────────────────
           18:00     0      0     0     14     1     12
           19:00     0      2     5     16     4     15
───────────────────────────────────────────────────────
           ИТОГО     1      5     7     39     7     36
                     err    n
           ВСЕГО    15     80
```

- `err` — количество ошибок (5xx + таймауты, 429/4xx НЕ считаются)
- `n` — всего запросов за период
- Цвет: зелёный (0 ошибок), жёлтый (есть), красный (>30%)

## Cron (каждые 15 минут)

```
*/15 * * * * cd ~/zen-monitor && python3 ./zen_monitor.py --log
```

## Все флаги

| Флаг | Описание |
|------|----------|
| `--models M` | Какие модели проверять (через запятую, переопределяет дефолт) |
| `-a, --add M` | Добавить модель для этого запуска |
| `--model M` | Фильтр отчёта (показать только эти модели) |
| `--report` | Отчёт за последние N часов |
| `--by-hour` | Группировка по часам |
| `--hours N` | Период отчёта (по умолч. 12) |
| `--date YYYY-MM-DD` | Дата для отчёта |
| `--time HH:MM` | Час для просмотра (с --errors) |
| `--errors` | Детали ошибок |
| `--json` | Вывод в валидный JSON |
| `--log [FILE]` | Дополнить JSON-массив (для cron) |
| `--daemon M` | Запустить демон с интервалом N минут |
| `--quiet` | Без прогресса, только результат |
| `--help` | Справка |

## Данные

- База: `~/zen-monitor/zen_data.db` (таблица checks)
- Лог: `~/zen-monitor/zen_monitor.json` (валидный JSON-массив)
- Cron: каждые 15 минут

## Инструкция для J.A.R.V.I.S. (оркестратор)

При запросе сэра о статистике нагрузки OpenCode моделей:
- **Всегда** используй период **12 часов** (`--hours 12`), если сэр не указал иное
- Команда по умолчанию: `python3 ./zen_monitor.py --report --by-hour --hours 12`
- Для просмотра ошибок: `python3 ./zen_monitor.py --errors --hours 12`
