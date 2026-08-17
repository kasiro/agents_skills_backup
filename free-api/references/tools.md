# Инструменты: FreeLLMAPI (агрегатор) и models.dev (поиск)

## FreeLLMAPI — Open Source агрегатор

| Параметр | Значение |
|----------|----------|
| **GitHub** | [github.com/tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) |
| **Формат** | OpenAI-compatible (самостоятельный хостинг) |
| **Лицензия** | MIT, TypeScript/Node.js |

**Фишки:**
- Объединяет 16+ бесплатных провайдеров в один endpoint
- Автоматический fallback между провайдерами
- Провайдеры: Groq, Gemini, Mistral, Cerebras, NVIDIA NIM, Cloudflare, GitHub Models, Ollama и др.
- Суммарно ~1.7 млрд токенов/мес

---

## Поиск бесплатных моделей через models.dev

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://models.dev/api.json` |
| **Формат** | JSON API |
| **Лимиты** | Нет (публичный endpoint) |

**Использование:**
```bash
# Поиск бесплатных моделей (сортировка по стоимости input токенов)
curl "https://models.dev/api.json?sort=input-costper&order=asc&search=FREE" | jq | head -200

# Поиск по конкретной модели
curl "https://models.dev/api.json?search=deepseek" | jq | head -100
```

**Фишки:**
- Параметр `search=FREE` — фильтр по FREE-тегу
- `sort=input-costper&order=asc` — от дешёвых к дорогим
- Возвращает: model ID, провайдер, лимиты контекста, стоимость, тип (FREE/PAID)
- Можно комбинировать с model-researcher для добавления найденных моделей в opencode.json
- **Запасной вариант:** если официальная документация провайдера недоступна — проверить модель через models.dev
