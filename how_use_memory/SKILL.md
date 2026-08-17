---
name: how_use_memory
description: |-
  Полный справочник памяти J.A.R.V.I.S. — memory blocks через
  memory_set/memory_replace/memory_list.
  Используй когда нужно понять как работает память, сохранить знание,
  найти информацию, диагностировать проблемы с памятью.

  Examples:
  - user: "как работает память" → memory blocks (этот файл)
  - user: "найди в памяти" → перечитать нужный блок из контекста
  - user: "сохрани это" → memory_set/memory_replace в подходящий блок
  - user: "консолидируй память" → пересмотр блоков вручную
  - user: "проверь память" → memory_list + проверка размеров блоков
---

# Память J.A.R.V.I.S. — memory blocks

## Как устроена память
- memory blocks: memory_set (перезапись блока), memory_replace (точечная правка), memory_list (список).
- Блоки: persona, human, project, knowledge, lessons. Scopes: global + project.
- Memory blocks всегда видны в системном промпте — поиск не нужен; при неуверенности — memory_list.

## Поиск (RECALL)
- Блоки уже в контексте. Если нужно вспомнить — перечитай нужный блок (persona/human/project/knowledge/lessons).
- Если не уверен в факте — перекрёстно проверь блоки (knowledge ↔ lessons ↔ project).

## Запись (SAVE)
- J.A.R.V.I.S. пишет НАПРЯМУЮ: memory_set (новый блок/полная замена) или memory_replace (точечная замена).
- Куда писать:
  - урок из ошибки/коррекции сэра → lessons: «- [YYYY-MM-DD] что произошло → что делать вместо»
  - архитектурное решение → project (scope global, секция Architecture decisions)
  - техническое знание/находка → knowledge (scope global)
  - правила проекта → project
  - личное о сэре → human
- Общие правила: одна запись 1-2 строки, с датой [YYYY-MM-DD]; не записывать очевидное; если сэр сказал «не записывай» — не писать.

## Консолидация
- Пересмотр memory blocks вручную: объединить дубли, почистить устаревшее, перенести важное между блоками (memory_set/memory_replace).
- Периодически (при завершении крупных задач): проверять lessons/knowledge на полноту.

## Диагностика
- memory_list — показать блоки и их размеры (chars_current/limit).
- Если блок переполнен (chars близко к limit) — почистить через memory_set, оставить только высокосигнальное.

## Примеры
- user: «как работает память» → объяснить memory blocks (этот файл)
- user: «сохрани это» → memory_set/memory_replace в подходящий блок
- user: «запомни идею» → memory_set label=knowledge или отдельная запись
- user: «консолидируй память» → пересмотр блоков вручную
- user: «какие у меня есть правила» → перечитать project (Rules) и human
