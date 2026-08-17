---
name: free-api
description: |-
  Справочник бесплатных LLM API провайдеров (free-tier и trial-кредиты) из репозитория cheahjs/free-llm-api-resources.
  API endpoints, лимиты, модели, форматы аутентификации и интеграции.
  Использовать когда нужен бесплатный API для LLM, найти альтернативу платному провайдеру,
  сравнить лимиты разных сервисов, настроить подключение к free API.

  Examples:
  - user: "какие есть бесплатные API для GPT-5?" → GitHub Models
  - user: "нужен бесплатный Llama 3.3" → Groq, Cerebras, Cloudflare, Scaleway
  - user: "сравни лимиты OpenRouter и Groq" → OpenRouter: 50 req/day, Groq: 1000-14400 req/day
  - user: "как подключиться к Google AI Studio" → API key + Google AI SDK endpoint
  - user: "какие модели есть на Cloudflare Workers AI" → список моделей с префиксом @cf/
---

# Бесплатные LLM API — Free API Resources

Справочник по бесплатным провайдерам LLM API на основе репозитория [cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources).
README репозитория авто-генерируется ежедневно (cron 00:00 UTC) — актуальные лимиты и модели всегда на GitHub.

Подробности по каждому провайдеру — в `references/` (progressive disclosure).

## 🗂️ Провайдеры → references

| Провайдер | Тип | Ключевое | Reference |
|-----------|-----|----------|-----------|
| **OpenRouter** | Free Tier | OpenAI-совместимый, 23 модели, 50 req/day | [openrouter.md](references/openrouter.md) |
| **Google AI Studio** | Free Tier | Gemini Flash + Gemma, 250K tok/min | [google-ai-studio.md](references/google-ai-studio.md) |
| **Groq** | Free Tier | Llama 3.3, GPT-OSS, до 14,400 req/day | [groq-cerebras.md](references/groq-cerebras.md) |
| **Cerebras** | Free Tier | GPT-OSS-120B, 14.4K req/day | [groq-cerebras.md](references/groq-cerebras.md) |
| **NVIDIA NIM** | Free Tier | 40 req/min, phone verification | [nvidia-nim.md](references/nvidia-nim.md) |
| **Mistral** | Free Tier | 1 req/s, 1B tok/month | [mistral.md](references/mistral.md) |
| **Mistral Codestral** | Free Tier | 30 req/min, 2,000 req/day | [mistral.md](references/mistral.md) |
| **HuggingFace** | Free Tier | $0.10/month credits | [other-free-tier.md](references/other-free-tier.md) |
| **Vercel AI Gateway** | Free Tier | $5/month, роутер | [other-free-tier.md](references/other-free-tier.md) |
| **OpenCode Zen** | Free Tier | deepseek-v4-flash-free и др., без кредитки | [zen.md](references/zen.md) |
| **Cohere** | Free Tier | 20 req/min, 1,000 req/month | [other-free-tier.md](references/other-free-tier.md) |
| **GitHub Models** | Free Tier | GPT-5, Llama, Phi; Copilot tier | [github-models.md](references/github-models.md) |
| **Cloudflare Workers AI** | Free Tier | 10,000 neurons/day, модели @cf/ | [cloudflare-ai.md](references/cloudflare-ai.md) |
| **BazaarLink** | Free Tier | 10 RPM, 150 req/day, саморегистрация | [other-free-tier.md](references/other-free-tier.md) |
| **Fireworks, Baseten, Nebius, Novita, AI21, Upstage, NLP Cloud, Alibaba, Modal, Inference.net, Hyperbolic, SambaNova, Scaleway** | Trial | $0.50–$30 кредиты | [trial-providers.md](references/trial-providers.md) |

## 📊 Сводка ключевых лимитов (быстрый справочник)

| Провайдер | Лимиты |
|-----------|--------|
| OpenRouter | 20 req/min, 50 req/day (до 1000/day при $10 lifetime topup) |
| Google AI Studio | Flash: 250K tok/min, 20 req/day; Gemma 3: 14,400 req/day |
| Groq | 250–14,400 req/day, 6K–70K tok/min |
| Cerebras | 30 req/min, 60K tok/min, 14.4K req/day |
| NVIDIA NIM | 40 req/min |
| Mistral | 1 req/s, 500K tok/min, 1B tok/month |
| Codestral | 30 req/min, 2,000 req/day |
| Cohere | 20 req/min, 1,000 req/month |
| GitHub Models | крайне ограниченные input/output token limits |
| Cloudflare | 10,000 neurons/day |
| BazaarLink | 10 RPM, 150 req/day |

## 🔧 Форматы API

| Формат | Провайдеры |
|--------|------------|
| **OpenAI-compatible** | OpenRouter, Groq, Cerebras, NVIDIA NIM, Mistral, Hyperbolic, SambaNova, Scaleway, Fireworks, Nebius, Baseten, Novita, GitHub Models, BazaarLink |
| **Google AI SDK** | Google AI Studio (свой endpoint) |
| **Cloudflare-specific** | Workers AI (свой формат `/accounts/{id}/ai/run/`) |
| **Cohere SDK** | Cohere (собственная библиотека) |

Подробнее — [api-formats.md](references/api-formats.md).

## 📝 Примечания

- **Phone verification** требуется у: NVIDIA NIM, Mistral, NLP Cloud
- **Data training opt-in** у: Google AI Studio (вне UK/CH/EEA/EU), Mistral, OpenCode Zen
- Некоторые провайдеры (Vertex AI, OVH, Lambda Labs, Kluster, Chutes) в разработке

## 🔗 Инструменты и ссылки

- **FreeLLMAPI** — Open Source агрегатор 16+ провайдеров (Groq, Gemini, Mistral, Cerebras, NVIDIA NIM, Cloudflare, GitHub Models, Ollama и др.), ~1.7 млрд токенов/мес: [github.com/tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi)
- **models.dev** — поиск бесплатных моделей: `curl "https://models.dev/api.json?search=FREE" | jq` (см. [tools.md](references/tools.md))
- Репозиторий: [github.com/cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources)
- OpenRouter: [openrouter.ai](https://openrouter.ai)
- Google AI Studio: [aistudio.google.com](https://aistudio.google.com)
- Groq Console: [console.groq.com](https://console.groq.com)
- GitHub Models: [github.com/marketplace/models](https://github.com/marketplace/models)
- Cloudflare Workers AI: [developers.cloudflare.com/workers-ai](https://developers.cloudflare.com/workers-ai)
- HuggingFace Inference: [huggingface.co/inference-providers](https://huggingface.co/inference-providers)
