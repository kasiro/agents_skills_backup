# Cloudflare Workers AI — Free Tier

| Параметр | Значение |
|----------|----------|
| **Endpoint** | `https://api.cloudflare.com/client/v4/accounts/{id}/ai/run/` |
| **API Format** | Cloudflare-specific |
| **Auth** | Cloudflare API Key + Account ID |
| **Лимиты** | 10,000 neurons/day |

## Модели (с префиксом @cf/)

- `@cf/aisingapore/gemma-sea-lion-v4-27b-it`
- `@cf/google/gemma-4-26b-a4b-it`
- `@cf/ibm-granite/granite-4.0-h-micro`
- `@cf/moonshotai/kimi-k2.6` / `kimi-k2.7-code`
- `@cf/nvidia/nemotron-3-120b-a12b`
- `@cf/openai/gpt-oss-120b` / `gpt-oss-20b`
- `@cf/qwen/qwen3-30b-a3b-fp8`
- `@cf/zai-org/glm-4.7-flash` / `glm-5.2`
- DeepSeek R1 Distill Qwen 32B
- Gemma 2B/7B, Llama 2 7B (LoRA)
- Llama 3.1 8B, 3.2 (1B/3B/11B Vision), 3.3 70B, 4 Scout
- Mistral 7B, Mistral Small 3.1 24B
- Qwen 2.5 Coder 32B, Qwen QwQ 32B
- Llama Guard 3 8B

## Ссылки

- [developers.cloudflare.com/workers-ai](https://developers.cloudflare.com/workers-ai)
