---
name: self-learning-kit
description: |-
  Общее хранилище полезных материалов от сэра. Сохраняет статьи, туториалы, фреймворки,
  инструменты, код, ссылки и любую полезную информацию в ~/self-learning/.
  Ведёт историю добавлений для проверки на дубликаты. Консолидирует знания через memory систему.
  Use proactively for: любые полезные материалы, которые сэр скидывает — статьи, GitHub репозитории,
  X/Twitter посты, документация, код, туториалы, исследования.
  
  Examples:
  - user: "вот статья по X" → проверить на дубликат, изучить, сохранить в соответствующую папку
  - user: "сохрани этот репозиторий" → изучить через deepwiki, сохранить в frameworks/
  - user: "обучи меня по X" → загрузить материалы из папки, создать план обучения
  - user: "найди в хранилище материалы по X" → поиск по ~/self-learning/
  - user: "что у нас есть по теме X?" → показать релевантные файлы из хранилища
---

# Self-Learning Kit — Общее хранилище полезных материалов

## Назначение
Хранилище ВСЕГО полезного, что сэр скидывает: статьи, репозитории, туториалы,
инструменты, документация, код, ссылки. Не только обучение — ВСЁ полезное.

## ⚠️ ПРОВЕРКА НА ДУБЛИКАТЫ — ОБЯЗАТЕЛЬНО

**ПЕРЕД сохранением каждого нового материала ОБЯЗАТЕЛЬНО проверяй историю добавлений ниже!**

### Как проверять:
1. Извлеки URL материала, который сэр скинул
2. Сверь с секцией «История добавлений» ниже
3. Если URL (или его ключевая часть) уже есть — **НЕ сохраняй**, а сообщи сэру: "Сэр, этот материал уже есть в хранилище: [ссылка на файл]"
4. Если URL новый — продолжай обработку

### Дополнительные проверки на дубликаты:
- По **названию статьи/репозитория** — даже если URL разный, но название совпадает
- По **автору + тема** — если автор тот же и тема та же
- По **ключевым словам в URL** — например, `reflexion` встречается в разных ссылках

### Формат записи в историю:
После успешного добавления материала ВСЕГДА добавляй новую строку в секцию «История добавлений»:

```
| ДД.ММ.ГГГГ | [URL](url) | Название | Папка/файл |
```

---

## История добавлений

Веди полный список обработанных ссылок. Это основа для проверки на дубликаты.

| Дата | URL | Название | Файл |
|------|-----|----------|------|
| 02.07.2026 | [arxiv.org/abs/2606.24937](https://arxiv.org/abs/2606.24937) | The Hitchhiker's Guide to Agentic AI | papers/arxiv-2606.24937-README.md |
| 02.07.2026 | [taskade.com/blog/self-improving-ai-agents-reflection](https://www.taskade.com/blog/self-improving-ai-agents-reflection) | Self-Improving AI Agents: The Reflection Loop (2026) | tutorials/taskade-reflection-loop-2026-README.md |
| 02.07.2026 | [x.com/akshay_pachaar/status/2069118430582866051](https://x.com/akshay_pachaar/status/2069118430582866051) | Stop Prompting, Start Engineering Loops | tutorials/x-akshay-harness-loops.md |
| 02.07.2026 | [github.com/nexu-io/harness-engineering-guide](https://github.com/nexu-io/harness-engineering-guide) | Harness Engineering Guide | frameworks/harness-engineering-guide.md |
| 02.07.2026 | [github.com/ksimback/looper](https://github.com/ksimback/looper) | Looper — Design-First Agent Loop Scaffolder | frameworks/looper.md |
| 02.07.2026 | [arxiv.org/abs/2606.27226](https://arxiv.org/abs/2606.27226) | Ask, Don't Judge: BINEVAL — interpretable LLM evaluation & self-improvement | papers/arxiv-2606-27226-binieval.md |
| 02.07.2026 | [huggingface.co/deepseek-ai/DeepSeek-V4-Pro-DSpark](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-DSpark) | DeepSeek-V4-Pro-DSpark — 1.6T MoE, 1M context, speculative decoding | frameworks/deepseek-v4-pro-dspark.md |
| 02.07.2026 | [github.com/NVlabs/Eagle/tree/main/Embodied](https://github.com/NVlabs/Eagle/tree/main/Embodied) | Eagle LocateAnything — vision-language grounding, Parallel Box Decoding | frameworks/eagle-embodied-locateanything.md |
| 02.07.2026 | [github.com/THUDM/slime](https://github.com/THUDM/slime) | Slime — LLM post-training RL framework (Megatron + SGLang) | frameworks/slime-rl-training.md |
| 02.07.2026 | [x.com/ataiiam/status/2069797329809395978](https://x.com/ataiiam/status/2069797329809395978) | Memory Architectures: Letta vs OpenClaw — frozen weights, plain text memory | tutorials/x-ataiiam-memory-architectures.md |
| 02.07.2026 | [github.com/alibaba/zvec](https://github.com/alibaba/zvec) | zvec — Alibaba Vector Library | frameworks/zvec.md |
| 02.07.2026 | [скриншот от сэра] | Agent Web Tools: SearXNG → Firecrawl → Camofox | references/agent-web-tools-stack.md |
| 02.07.2026 | [собственный анализ] | Анализ архитектуры J.A.R.V.I.S. через собранные материалы | notes/jarvis-architecture-analysis.md |
| 02.07.2026 | [собственный план] | План закрытия пробелов J.A.R.V.I.S. (6 решений) | notes/jarvis-gap-closure-plan.md |
| 02.07.2026 | [собственный план v2] | План закрытия пробелов J.A.R.V.I.S. V2 — архитектурные кластеры (3 фазы) | notes/jarvis-gap-closure-plan-v2.md |
| 02.07.2026 | [walkinglabs.github.io/learn-harness-engineering/](https://walkinglabs.github.io/learn-harness-engineering/en/) | Learn Harness Engineering — полный курс (12 лекций) | tutorials/learn-harness-engineering-course.md |
| 02.07.2026 | [twotimespi.dev](https://twotimespi.dev) | Tau — educational Python coding agent (3-layer architecture) | frameworks/tau-coding-agent.md |
| 02.07.2026 | [langchain.com/blog/the-anatomy-of-an-agent-harness](https://langchain.com/blog/the-anatomy-of-an-agent-harness) | Anatomy of an Agent Harness — Agent = Model + Harness | tutorials/anatomy-of-an-agent-harness-langchain.md |
| 02.07.2026 | [humanlayer.dev/blog/skill-issue-harness-engineering](https://humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) | Skill Issue: Harness Engineering for Coding Agents | tutorials/humanlayer-skill-issue-harness-engineering.md |
| 29.07.2026 | [arxiv.org/abs/2607.14159](https://arxiv.org/abs/2607.14159) | MemoHarness: Agent Harnesses That Learn from Experience | papers/arxiv-2607-14159-memoharness.md |

---

## Структура хранилища

Все материалы сохраняются в `~/self-learning/`:

```
~/self-learning/
├── README.md              # Описание хранилища
├── papers/                # Научные статьи, исследования, arXiv
├── tutorials/             # Туториалы, руководства, blog posts
├── frameworks/            # Фреймворки, библиотеки, модели
├── tools/                 # Утилиты, CLI tools, скрипты
├── articles/              # Статьи, посты (не научные)
├── notes/                 # Заметки и конспекты
├── projects/              # Практические проекты
└── references/            # Справочные материалы, доки
```

## Процесс обработки нового материала

### Шаг 1: Проверка на дубликат
- Свери URL с «Историей добавлений» выше
- Проверь по названию, автору+теме, ключевым словам в URL
- Дубликат → сообщи сэру и НЕ сохраняй

### Шаг 2: Сбор материала
- Статья arXiv → lightpanda для аннотации/PDF
- YouTube видео → youtube-transcript для транскрипта
- GitHub репозиторий → deepwiki для документации
- Веб-страница → lightpanda для парсинга
- X/Twitter пост → lightpanda для контента

### Шаг 3: Классификация
Определи тип материала:
- `papers/` — научные статьи, исследования, arXiv
- `tutorials/` — руководства, уроки, blog posts, X/Twitter посты
- `frameworks/` — фреймворки, библиотеки, модели, репозитории
- `tools/` — утилиты, CLI tools, скрипты
- `articles/` — статьи, обзоры (не научные)
- `notes/` — собственные заметки и конспекты
- `projects/` — практические реализации
- `references/` — справочники, документация, схемы

### Шаг 4: Сохранение
Создай README-файл в соответствующей папке с:
- Метаданные (автор, дата, источник, лицензия)
- Краткая аннотация (2-5 предложений)
- Ключевые концепции (список)
- Основные тезисы (структурировано)
- Связи с другими материалами (cross-references)

### Шаг 5: Консолидация в память
После сохранения:
1. Сохрани ключевые инсайты в lessons
2. Создай memory save с типом "pattern" или "fact"
3. Используй `consolidate(tier="semantic")` для интеграции

## Быстрые команды

| Действие | Описание |
|----------|----------|
| `~/self-learning/` | Корень хранилища |
| `ls ~/self-learning/papers/` | Список статей |
| `ls ~/self-learning/tutorials/` | Список туториалов |
| `ls ~/self-learning/frameworks/` | Список фреймворков |
| `ls ~/self-learning/tools/` | Список инструментов |
