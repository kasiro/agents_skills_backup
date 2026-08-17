# Groq + Cerebras — Free Tier (быстрые инференс-провайдеры)

Оба провайдера — OpenAI-compatible, API Key.

## Groq

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://api.groq.com/openai/v1` |
| **API Format** | OpenAI-compatible |
| **Auth** | API Key |

### Модели и лимиты

| Модель | req/day | tok/min |
|--------|---------|---------|
| Allam 2 7B | 7,000 | 6,000 |
| Llama 3.1 8B | 14,400 | 6,000 |
| Llama 3.3 70B | 1,000 | 12,000 |
| Llama 4 Scout Instruct | 1,000 | 30,000 |
| GPT-OSS 120B / 20B | 1,000 | 8,000 |
| Qwen3 32B | 1,000 | 6,000 |
| Qwen3.6 27B | 1,000 | 8,000 |
| Whisper Large v3 / v3 Turbo | 2,000 | — |
| Groq Compound / Mini | 250 | 70,000 |

## Cerebras

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://api.cerebras.ai/v1` |
| **API Format** | OpenAI-compatible |

### Модели и лимиты

| Модель | Лимиты |
|--------|--------|
| GPT-OSS-120B | 30 req/min, 60K tok/min, 900 req/hr, 1M tok/hr, 14.4K req/day, 1M tok/day |
| Llama 3.1 8B | те же |

## Ссылки

- Groq Console: [console.groq.com](https://console.groq.com)
