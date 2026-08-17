# DECISION MATRIX — быстрый выбор инструмента

| Ситуация | Инструмент |
|----------|-----------|
| Вспомнить прошлое | просмотр memory blocks (в системном промпте), при неуверенности — `memory_list` |
| Сохранить важное | `memory_set` / `memory_replace` (блок knowledge/project по смыслу) |
| Урок из ошибки | `memory_set` label=lessons |
| Найти уроки | просмотр memory blocks / `memory_list` |
| Доки библиотек | `context7` |
| Веб-поиск / исследование | `lightpanda` (Bing через fetch) — единственный канал |
| GitHub репозиторий | `deepwiki` |
| Читать файл | `read` |
| Сложная подзадача | `task(background=true)` + сабагент |
| Проверить статус фоновых сабагентов | `get_subagents_in_background` (по Background Monitor Protocol) |
| Завершить зависшего фонового сабагента | `stop_subagent(task_id=...)` (по Background Monitor Protocol) |
| Непонятно | `question` |
| **Структурировать задачу** | **→ CYCLE 1.5 Task Intake** (task-intake.md) |
| **Автономно выполнить** | **→ CYCLE 2.5 Autonomous Execution** (autonomous-execution.md) |
| **Разбить на подзадачи** | **CYCLE 1.5 → Decompose → sequential-thinking** (task-intake.md) |
| **Проверить результат шага** | **CYCLE 2.5 → Verify (таблица)** (autonomous-execution.md) |
| **Post-mortem задачи** | **CYCLE 2.5 → Post-execution Reflection** (autonomous-execution.md) |
| **Понять уверенность** | **CYCLE 1.5 → Confidence Check → Confirm** (task-intake.md) |

## Навигация по протоколам

| Что нужно | Куда смотреть |
|-----------|--------------|
| Per-message цикл | cycle1.md |
| Понимание/декомпозиция задачи | task-intake.md |
| Автономное выполнение + делегирование | autonomous-execution.md |
| Старт/конец сессии | cycle3.md |
| Выбор инструмента | этот файл (decision-matrix.md) |
| Работа с памятью | memory-protocol.md |
| Улучшение себя | self-improvement.md |
| Проверка фактов | accuracy-protocol.md |
| Фоновые сабагенты | background-monitor.md |
