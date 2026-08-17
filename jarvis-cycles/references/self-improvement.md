# 🔧 SELF-IMPROVEMENT

## Триггеры
- **Сэр исправил** → `memory_set` label=lessons (урок)
- **Сэр сказал «запомни»** → `memory_set` label=knowledge (запись)
- **Найдено улучшение скилла** → EDIT SKILL.md → git add/commit
- **Старт сессии** → memory blocks уже в системном промпте (блок lessons — уроки прошлых сессий)

## Инструменты
- `memory_list` / просмотр memory blocks — поиск уроков (только чтение!)
- Запись в память напрямую через `memory_set` (label=lessons/knowledge) / `memory_replace`
- `git add -A && git commit -m "update: {skill_name}"` — закоммитить изменения

## Автоматический self-improvement (без напоминаний)

Всё происходит автоматически, сэр ничего не должен напоминать:

1. **Я ошибся** → `memory_set` label=lessons
2. **Повторил ошибку** → улучшение SKILL.md → git add/commit
3. **Нашёл лучший способ** → update SKILL.md → git add/commit
4. **Сэр исправил** → `memory_set` label=lessons

## Проактивный аудит (Auto-Detect)

Периодический self-check без сигнала от сэра:
- Раз в 20-30 сессий (или при CYCLE 3 END): запуск анализа tool calls на ошибки
  `sqlite3 ~/.local/share/opencode/opencode.db "SELECT json_extract(data, '$.tool') as tool, json_extract(data, '$.state.input.error') as error, datetime(e.created_at/1000, 'unixepoch', 'localtime') as time FROM event e WHERE json_extract(data, '$.type') = 'part' AND json_extract(data, '$.tool') = 'invalid' ORDER BY e.created_at DESC LIMIT 20;"`
- Найденные invalid/ошибки → анализ: это системная проблема или разовая?
- Результаты → `memory_set` label=lessons (или knowledge — системные паттерны)
- Если один и тот же тип ошибки повторяется 3+ раз → предложить улучшение скилла/протокола

Никаких напоминаний. Система работает в фоне, я сам отслеживаю свои ошибки.
