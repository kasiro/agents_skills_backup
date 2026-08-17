# Форматы API — аутентификация и интеграция

| Формат | Провайдеры |
|--------|------------|
| **OpenAI-compatible** | OpenRouter, Groq, Cerebras, NVIDIA NIM, Mistral, Hyperbolic, SambaNova, Scaleway, Fireworks, Nebius, Baseten, Novita, GitHub Models, BazaarLink |
| **Google AI SDK** | Google AI Studio (свой endpoint) |
| **Cloudflare-specific** | Workers AI (свой формат `/accounts/{id}/ai/run/`) |
| **Cohere SDK** | Cohere (собственная библиотека) |

## Особенности аутентификации

| Тип | Провайдеры |
|-----|------------|
| API Key | OpenRouter, Google AI Studio, Groq, Cerebras, HuggingFace, Cohere, GitHub Models, Cloudflare (Key + Account ID), BazaarLink, OpenCode Zen |
| Phone verification | NVIDIA NIM, Mistral, NLP Cloud |
| Подписка/tier | GitHub Models (Copilot tier), Mistral Codestral (monthly subscription) |
| Саморегистрация агентов | BazaarLink (`/api/v1/agents/register`) |

**⚠️ Data training opt-in** у: Google AI Studio (вне UK/CH/EEA/EU), Mistral, OpenCode Zen
