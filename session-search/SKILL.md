---
name: session-search
description: |-
  Просмотр и поиск сессий OpenCode через SQLite. Список сессий, полнотекстовый поиск (FTS5) по содержимому сообщений с поддержкой отдельных слов и словосочетаний, инспекция сессии. Использует `ses` CLI + `ocdb`. Use proactively when user asks to look up past sessions, search conversation history, review what was done before, or find a specific session.

  Examples:
  - user: "найди сессию про auth" → ses search auth
  - user: "покажи последние сессии" → ses list
  - user: "что мы делали с docker compose" → ses search "docker compose"
  - user: "проверь сессию ses_abc123" → ses inspect ses_abc123
  - user: "найди сессии за сегодня" → ses list --today
  - user: "поиск по точной фразе" → ses fts "\"точная фраза\""
  - user: "найди где обсуждали API keys и rate limiting" → ses fts "API keys AND rate limiting"
  - user: "покажи сессии в формате таблицы" → ses list --table
---
# Session Search — просмотр и поиск сессий OpenCode

Скилл для поиска по истории сессий OpenCode. Позволяет просматривать список сессий, искать по содержимому сообщений (слова и словосочетания), инспектировать детали сессий.

## Быстрый старт

```bash
ses list                  # последние 20 сессий
ses search "query"        # поиск по содержимому
ses inspect <id>          # детали сессии
ses fts "слово"           # полнотекстовый поиск (FTS5)
ses help                  # все команды
```

## Команды

### `ses list` — список сессий
```
ses list                # последние 20 (по умолчанию)
ses list --limit 50     # последние 50
ses list --all          # все сессии (без лимита)
ses list --today        # сессии за сегодня
ses list --table        # табличный вывод
ses list --json         # JSON вывод
ses list --project      # фильтр по текущему проекту
```

### `ses search <query>` — поиск по содержимому
Ищет по заголовкам сессий и содержимому сообщений. Поддерживает отдельные слова и словосочетания.

```
ses search "auth"                    # поиск слова
ses search "docker compose"          # поиск словосочетания
ses search "refactor" --limit 10     # максимум 10 результатов
ses search "config" --table          # табличный вывод
ses search "bug fix" --json          # JSON вывод
ses search "api" --project           # только текущий проект
ses search "deploy" --days 7         # последние 7 дней
```

### `ses inspect <id>` — детали сессии
Показывает полную информацию о сессии: метаданные, сообщения, todos, токены, стоимость.

```
ses inspect ses_abc123
ses inspect ses_abc123 --messages 5   # показать последние 5 сообщений
ses inspect ses_abc123 --todos        # только todos
ses inspect ses_abc123 --json         # JSON вывод
```

### `ses fts <query>` — полнотекстовый поиск FTS5
Продвинутый поиск через виртуальную таблицу FTS5. Поддерживает булевы операторы.

```
ses fts "auth"                        # поиск слова
ses fts "\"rate limiting\""           # точная фраза (кавычки)
ses fts "auth AND jwt"                # оба слова (AND)
ses fts "auth OR jwt"                 # любое из слов (OR)
ses fts "auth NOT oauth"              # исключить слово (NOT)
ses fts "auth NEAR/3 jwt"             # слова в пределах 3 токенов
ses fts "auth*"                       # префикс (auth, auth0, authz...)
ses fts "api key" --project           # только текущий проект
ses fts "deploy" --days 30            # последние 30 дней
```

### `ses filter` — фильтр сессий через GraphQL
Фильтрация через GraphQL API ocdb. Поддерживает поиск по заголовкам, содержимому, агенту, модели и датам.

```
ses filter --search "docker compose"        # поиск по заголовку и сообщениям
ses filter --title-substring "auth"         # по подстроке в заголовке
ses filter --agent jarvis --limit 10        # по агенту
ses filter --model gpt --days 7             # по модели за последние 7 дней
ses filter --search "error" --agent jarvis  # комбинированный фильтр
ses filter --search "deploy" --json         # JSON вывод
```

**Аргументы:**
| Флаг | Описание |
|------|----------|
| `-s`, `--search` | Полнотекстовый поиск (заголовок + содержимое сообщений) |
| `-t`, `--title-substring` | Подстрока в заголовке |
| `-a`, `--agent` | Фильтр по агенту |
| `-m`, `--model` | Подстрока в модели |
| `-i`, `--session-id` | Подстрока в ID сессии |
| `--min-msgs` | Мин. кол-во сообщений |
| `--min-input` | Мин. входных токенов |
| `--min-output` | Мин. выходных токенов |
| `--date-from` | От даты (YYYY-MM-DD) |
| `--date-to` | До даты (YYYY-MM-DD) |
| `--order-by` | Поле сортировки |
| `--order-dir` | Направление (asc/desc) |

### `ses ocdb [args]` — передача аргументов в ocdb
Прокси-команда для вызова установленной утилиты ocdb.

```
ses ocdb sessions
ses ocdb session ses_abc123 --raw
```

### `ses ocdb-check` — проверка наличия ocdb
```
ses ocdb-check
```

### `ses stats` — статистика по сессиям
```
ses stats               # общая статистика
ses stats --by-project  # по проектам
ses stats --by-agent    # по агентам
ses stats --by-model    # по моделям
ses stats --days 7      # за последние 7 дней
```

### `ses db` — информация о БД
```
ses db              # путь и размер БД
ses db --tables     # список таблиц
ses db --size       # только размер
```

## Пайплайн

```
ses list | head -5  # первые 5 из списка
ses list --json | jq '.[] | .title'
ses search "query" --json | jq -r '.[] | "\\(.id): \\(.title)"'
```

## Интеграция с ocdb

Утилита `ocdb` (v0.1.0, Python/GraphQL) уже установлена в системе:
- `~/.local/bin/ocdb` — основная команда
- Поддерживает: `sessions`, `messages`, `dailyStats`, `modelStats`, `raw`

Скилл использует `ocdb` как дополнительный источник данных, но основной функционал поиска реализован через прямой доступ к SQLite (FTS5).

## База данных

- Путь: `~/.local/share/opencode/opencode.db`
- Технология: SQLite с Drizzle ORM
- FTS5: виртуальная таблица `sessions_fts` создаётся автоматически при первом поиске
