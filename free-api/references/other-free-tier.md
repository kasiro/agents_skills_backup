# Прочие Free Tier провайдеры — HuggingFace, Vercel, Cohere, BazaarLink

## HuggingFace Inference Providers

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://api-inference.huggingface.co/` |
| **Auth** | API Key |
| **Лимиты** | $0.10/month credits |
| **Модели** | Various open models (<10GB, некоторые популярные >10GB) |

**Ссылка:** [huggingface.co/inference-providers](https://huggingface.co/inference-providers)

---

## Vercel AI Gateway

| Параметр | Значение |
|----------|----------|
| **Endpoint** | Routes to various supported providers |
| **Лимиты** | $5/month |
| **Особенность** | Gateway/router к разным провайдерам |

---

## Cohere

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://api.cohere.com/v1` |
| **API Format** | Cohere SDK |
| **Лимиты** | 20 req/min, 1,000 req/month (общий пул) |

### Модели

- c4ai-aya-expanse-32b, c4ai-aya-vision-32b
- command-a-03-2025, command-a-plus-05-2026, command-a-reasoning-08-2025
- command-a-translate-08-2025, command-a-vision-07-2025
- command-r-08-2024, command-r-plus-08-2024
- command-r7b-12-2024, command-r7b-arabic-02-2025

---

## BazaarLink

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://api.bazaarlink.ai/v1/chat/completions` |
| **API Format** | OpenAI-compatible |
| **Auth** | API Key (саморегистрация агентов через `/api/v1/agents/register`) |
| **Кредитка** | Не требуется |
| **Лимиты** | 10 RPM, 150 req/day |

### Фишки

- Специальная модель `auto:free` — автоматически выбирает доступную бесплатную модель
- Программная регистрация агентов — агенты могут сами создавать себе API-ключи
