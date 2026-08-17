---
name: agent-delegation
description: |-
  Agent delegation system for J.A.R.V.I.S. — who does what. general (search + code + bash),
  explore (fast read-only navigation).
  Use proactively when a task matches an agent's specialization.
  
  Examples:
  - user: "напиши парсер для JSON" → delegate to general (code)
  - user: "найди новую библиотеку для PDF" → delegate to general (search+research)
  - user: "проверь нагрузку на диск" → delegate to general (bash diagnostics)
  - user: "отрефактори этот модуль" → delegate to general (code)
  - user: "исследуй структуру репозитория" → delegate to explore (fast read-only)
  - user: "найди баг в API и почини" → delegate to general (research+code)
---
# Agent Delegation System

## Правило: один вызов = один сабагент

Не отправляй две задачи разным агентам одновременно если они зависят друг от друга.

## Сабагенты: background vs foreground

**Background** (`task(background=true, ...)`) — задача не блокирует диалог:
- Работает параллельно, уведомит когда закончит
- Не занимает контекст основного агента
- Используй для: независимых исследований, диагностики, долгих операций (>30с)

**Foreground** (`task(..., background=false/unspecified)`) — ждём результат:
- Результат нужен перед продолжением
- Короткие задачи (<30с) где ответ влияет на следующие шаги
- Используй для: dependency (следующий шаг зависит от результата)

## Суб-агенты

### general — Универсальный агент
- **Инструменты:**
  - MCP: lightpanda_*, deepwiki_*, context7_*, youtube-transcript_*, sequential-thinking_*
  - Built-in: edit, bash, webfetch, read
- **Когда:** любая задача — поиск, код, bash, диагностика (в память НЕ пишет — это делает J.A.R.V.I.S. через memory blocks), или их комбинация
- **Лучше:** чем гадать какой агент выбрать — general всё умеет сам
- **Заменяет:** бывших researcher, executor, sysadmin

### explore — Быстрый навигатор
- **Инструменты:** rg, fd, bun (только read-only, быстрые аналоги)
- **Когда:** быстро посмотреть структуру проекта, найти файл, grep по коду
- **Самый лёгкий:** минимальное потребление контекста
- **Не давать:** редактирование, запуск команд, веб-поиск

## Decision Tree

```
Запрос сэра
├── Код / bash / поиск / диагностика / комбинация
│   → task(subagent_type="general") — foreground/background по ситуации
├── Быстрый поиск в проекте (read-only)
│   → task(subagent_type="explore") — foreground (быстро)
├── Операции с памятью: J.A.R.V.I.S. сам пишет в memory blocks (memory_set/memory_replace). Делегирование general — только для файлов (код, конфиги, отчёты).
└── Непонятно / нужна координация
    → делай сам (J.A.R.V.I.S.)
```

## Приоритет MCP инструментов

При исследовании/поиске использовать:

1. **lightpanda** — единственный рабочий канал (Bing через fetch, чтение страниц)

## Важно: background для долгих задач

- Если задача займёт >30с или >3 шагов — ставь `background=true`
- general справится с любой комбинацией: и поищет, и поправит, и запустит
- Не нужно разделять одну задачу на несколько вызовов — general сам решает какие инструменты использовать
