---
name: github-api-search
description: |-
  GitHub REST API через curl. Поиск репозиториев, чтение файлов/README, информация о репозитории, поиск кода, релизы, issues. Использовать когда нужен поиск по GitHub, проверка репозиториев, анализ кода, исследование open-source проектов.

  Examples:
  - user: "найди MCP сервера для Telegram" → curl api.github.com/search/repositories?q=telegram+mcp+server
  - user: "проверь репозиторий owner/repo" → curl api.github.com/repos/owner/repo
  - user: "прочитай README" → curl api.github.com/repos/owner/repo/readme
  - user: "найди код с keyword" → curl api.github.com/search/code?q=keyword
  - user: "посмотри релизы проекта" → curl api.github.com/repos/owner/repo/releases
---

# github-api-search — GitHub REST API через curl

## Аутентификация
- Без токена: 60 запросов/час
- С токеном: 5000/час

```bash
# Как прочитать токен (из auth.json или переменной окружения)
TOKEN=$(jq -r '.github.key // ""' ~/.local/share/opencode/auth.json 2>/dev/null || echo "${GITHUB_TOKEN:-}")
[ -n "$TOKEN" ] && AUTH="-H 'Authorization: Bearer $TOKEN'" || AUTH=""
```

## Эндпоинты

| Действие | URL | Описание |
|----------|-----|----------|
| Поиск репозиториев | `GET /search/repositories?q=...` | Поиск по имени, описанию, readme |
| Инфо о репозитории | `GET /repos/{owner}/{repo}` | Звёзды, лицензия, темы, язык |
| README | `GET /repos/{owner}/{repo}/readme` | README в base64 → декодировать |
| Содержимое файла | `GET /repos/{owner}/{repo}/contents/{path}` | Любой файл из репозитория |
| Поиск кода | `GET /search/code?q=...` | Поиск в коде репозиториев |
| Релизы | `GET /repos/{owner}/{repo}/releases` | Список релизов с тегами |
| Issues | `GET /repos/{owner}/{repo}/issues` | Открытые/закрытые issues |

## Примеры

### Поиск репозиториев
```bash
curl -s "https://api.github.com/search/repositories?q=telegram+mcp+server&sort=stars&order=desc&per_page=10" | jq '[.items[] | {name: .full_name, stars: .stargazers_count, desc: .description}]'
```

### Информация о репозитории
```bash
curl -s "https://api.github.com/repos/mcp-telegram/mcp-telegram" | jq '{name: .full_name, stars: .stargazers_count, license: .license.spdx_id, topics: .topics}'
```

### README (декодировать base64)
```bash
curl -s "https://api.github.com/repos/mcp-telegram/mcp-telegram/readme" | jq -r '.content' | base64 -d
```

### Содержимое файла
```bash
curl -s "https://api.github.com/repos/mcp-telegram/mcp-telegram/contents/package.json" | jq -r '.content' | base64 -d
```

### Поиск кода
```bash
curl -s "https://api.github.com/search/code?q=mcp+telegram+in:name&per_page=10" -H "Accept: application/vnd.github+json" | jq '[.items[] | {name: .name, repo: .repository.full_name, path: .path}]'
```

### Релизы
```bash
curl -s "https://api.github.com/repos/mcp-telegram/mcp-telegram/releases?per_page=10" | jq '[.[] | {tag: .tag_name, name: .name, prerelease: .prerelease, created: .created_at}]'
```

## Параметры запросов
- `?q=` — поисковый запрос
- `&sort=stars|updated|forks`
- `&order=desc|asc`
- `&per_page=N` (max 100)
- `&page=N`
- Квалификаторы: `in:name`, `in:description`, `in:readme`, `language:python`, `stars:>100`, `topic:mcp`

## Обработка ошибок
- **403** — rate limit (без токена 60/ч; с токеном 5000/ч)
- **404** — репозиторий/файл не найден
- **422** — неверный запрос
- **401** — плохой токен

Проверка HTTP кода:
```bash
curl -s -o /dev/null -w "%{http_code}\n" "https://api.github.com/repos/mcp-telegram/mcp-telegram"
```

Проверка rate limit:
```bash
curl -s "https://api.github.com/rate_limit" | jq '.rate'
```
