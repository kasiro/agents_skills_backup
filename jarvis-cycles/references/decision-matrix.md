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
| **Прошлые сессии («делал ли я…», «что решали про X»)** | **recall через `execute`** → раздел «Recall» ниже |

## Recall — поиск по прошлым сессиям

Плагин `recall` (`~/.config/opencode/plugins/recall/`) даёт 3 инструмента. Вызываются **только внутри `execute`** — прямым tool-вызовом недоступны.

| Инструмент | Что делает | Параметры |
|------------|-----------|-----------|
| `tools.recall_list` | последние сессии текущей директории | `limit` (по умолчанию 10), `includeChildren` (по умолчанию false) |
| `tools.recall_search` | поиск сессий по заголовку и агенту | `query` (обязателен), `limit` (10), `agent` (опционально) |
| `tools.recall_read` | сообщения конкретной сессии | `session_id` (обязателен), `limit` (не указан = все), `role` = user/assistant/system |

**Когда использовать:**
- «А делал ли я когда-то…», «что мы решали про X», «как тогда настроили Y»
- Нужен прошлый конфиг/команда/решение, которого нет в memory blocks
- Memory blocks ответа не дали, но тема явно обсуждалась ранее

**Когда НЕ использовать:** тема ещё в текущем контексте; факт есть в memory blocks (они всегда в промпте — это дешевле).

**Примеры (внутри `execute`):**

```javascript
const found = await tools.recall_search({ query: "waybar", limit: 5 })
const recent = await tools.recall_list({ limit: 20, includeChildren: false })
const msgs = await tools.recall_read({ session_id: "ses_abc123", limit: 20, role: "user" })
```

**Ограничения:**
- `list` и `search` видят только **текущую директорию** (`ctx.location.directory`) — сессии других проектов не находятся.
- `search` ищет **только по заголовку и агенту**, не по содержимому сообщений. Нужен факт из середины диалога → сначала `list`/`search` за ID, затем `recall_read`.
- `limit` по умолчанию 10; в `search` просматриваются до 100 последних сессий, затем обрезка по `limit`.
- `recall_read` без `limit` отдаёт все сообщения, с `limit` — **последние** N. Текст каждого сообщения обрезается до 200 символов.

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
