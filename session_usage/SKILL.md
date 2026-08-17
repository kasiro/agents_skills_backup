---
name: session-usage
description: |-
  Выгрузка и отображение статистики использования OpenCode — сессии, токены, модели.
  Фильтрация по дате/времени, модели, субагентам, минимальным значениям.
  Вывод: таблица, сводка по моделям/дням, JSON, CSV.
  Для быстрой статистики — ocdb stats/sessions (без установки зависимостей).
  Для детальных отчётов — opencode_usage_export.py (часы, категории, баланс).
  Использовать когда нужно посмотреть статистику сессий, расход токенов,
  проанализировать использование по моделям или субагентам.

  Examples:
  - user: "покажи статистику за сегодня" → ocdb sessions --today (быстро) или python3 ~/Документы/python_projects/opencode_usage_export.py --today (детально)
  - user: "сколько токенов за неделю" → ocdb sessions --days 7 --summary (быстро) или python3 ~/Документы/python_projects/opencode_usage_export.py --days 7 (детально)
  - user: "сессии через executor" → python3 ~/Документы/python_projects/opencode_usage_export.py --sessions --subagent executor
  - user: "общая статистика" → ocdb stats
  - user: "сводка по моделям" → ocdb stats --models (быстро) или python3 ~/Документы/python_projects/opencode_usage_export.py --days 7 --summary (детально)
  - user: "только человеческие сессии" → python3 ~/Документы/python_projects/opencode_usage_export.py --sessions --no-subagents
---
# Session Usage — Статистика OpenCode

Скрипт: `~/Документы/python_projects/opencode_usage_export.py`

## Быстрый вариант: ocdb

```bash
ocdb stats                       # общая статистика (сессии, токены, БД)
ocdb stats --models              # по моделям
ocdb stats --agents              # по агентам
ocdb sessions --today            # сессии за сегодня
ocdb sessions --days 7           # за неделю
ocdb sessions --agent executor   # фильтр по агенту
ocdb sessions --format json      # JSON вывод
```

Для быстрых запросов — ocdb. Для детальных отчётов (по часам, CSV-экспорт, баланс) — opencode_usage_export.py.

## Команды

```bash
# Быстрые итоги
python3 ~/Документы/python_projects/opencode_usage_export.py --today
python3 ~/Документы/python_projects/opencode_usage_export.py --days 7

# Таблица сессий
python3 ~/Документы/python_projects/opencode_usage_export.py --sessions --days 1

# Фильтры по субагентам
python3 ~/Документы/python_projects/opencode_usage_export.py --sessions --subagent executor
python3 ~/Документы/python_projects/opencode_usage_export.py --sessions --no-subagents
python3 ~/Документы/python_projects/opencode_usage_export.py --sessions --subagents-only

# Сводки
python3 ~/Документы/python_projects/opencode_usage_export.py --days 7 --summary          # по моделям
python3 ~/Документы/python_projects/opencode_usage_export.py --days 7 --by-day           # по дням

# По часам
python3 ~/Документы/python_projects/opencode_usage_export.py --by-hour
python3 ~/Документы/python_projects/opencode_usage_export.py --today --by-hour
python3 ~/Документы/python_projects/opencode_usage_export.py --date 2026-06-21 --by-hour

# Экспорт
python3 ~/Документы/python_projects/opencode_usage_export.py --days 30 --export usage.csv

# JSON
python3 ~/Документы/python_projects/opencode_usage_export.py --days 7 --json
```

## Фильтры

### По дате
| Флаг | Описание |
|------|----------|
| `--today` | Только сегодня |
| `--days N` | Последние N дней |
| `--date YYYY-MM-DD` | Точная дата |
| `--from YYYY-MM-DD` | Начало периода |
| `--to YYYY-MM-DD` | Конец периода |

### По времени
| Флаг | Описание |
|------|----------|
| `--time HH:MM` | Точное время |
| `--from-time HH:MM` | Начало временного окна |
| `--to-time HH:MM` | Конец временного окна |

### По субагентам
| Флаг | Описание |
|------|----------|
| `--subagent TYPE` | explore, executor, general, researcher, sysadmin |
| `--no-subagents` | Только человеческие сессии |
| `--subagents-only` | Только субагентские сессии |

### Прочие
| Флаг | Описание |
|------|----------|
| `--model MODEL` | Фильтр по модели (подстрока) |
| `--session-id SID` | Фильтр по ID сессии |
| `--nonzero` | Скрыть нулевые токены |
| `--min-msgs N`, `--min-input N`, `--min-output N` | Минимальные значения |
| `--min-cache-read N`, `--min-reasoning N` | Минимальные значения |

## Режимы вывода
| Флаг | Описание |
|------|----------|
| `--sessions` | Таблица сессий |
| `--summary` | Сводка по моделям |
| `--by-day` | Сводка по дням |
| `--by-hour` | Сводка по часам с гистограммой |
| `--json` | JSON-вывод |
| `--export FILE` | CSV-экспорт |
| `--compact` | Только итоги (по умолчанию) |

## Путь к данным
База данных OpenCode: `~/.local/share/opencode/opencode.db`
