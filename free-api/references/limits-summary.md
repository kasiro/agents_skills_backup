# Сводка лимитов по типам

| Тип лимита | Где встречается |
|------------|-----------------|
| **req/min** | OpenRouter (20), NVIDIA (40), Cohere (20), Cerebras (30), Mistral (60) |
| **req/day** | OpenRouter (50-1000), Groq (250-14,400), Google AI (10-500) |
| **tok/min** | Google AI (10K-250K), Groq (6K-70K), Cerebras (60K) |
| **tok/month** | Mistral (1B) |
| **neurons/day** | Cloudflare (10K) |
| **$ credit** | HuggingFace ($0.10), Vercel ($5), Fireworks ($1), Baseten ($30) и др. |

## Примечания

- **Phone verification** требуется у: NVIDIA NIM, Mistral, NLP Cloud
- **Data training opt-in** у: Google AI Studio (вне UK/CH/EEA/EU), Mistral, OpenCode Zen
- Репозиторий принимает только **легитимные сервисы** — reverse engineering исключён
- README авто-генерируется ежедневно (cron 00:00 UTC) — актуальные лимиты всегда на GitHub
- Некоторые провайдеры (Vertex AI, OVH, Lambda Labs, Kluster, Chutes) в разработке
