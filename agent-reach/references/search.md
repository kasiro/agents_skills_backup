# 搜索工具

网页搜索（lightpanda — Bing 通过 fetch）。

## 网页搜索

Единственный рабочий канал — lightpanda (Bing через fetch). Запрос URL-кодировать, пробелы → `+`.

```bash
lightpanda fetch "https://www.bing.com/search?q=<запрос>"
```

### 使用场景

| 场景 | 参数 |
|-----|------|
| 网页搜索 | `lightpanda fetch "https://www.bing.com/search?q=<запрос>"` |
| 读取页面 | `lightpanda markdown {url}` |

### 特点

- Bing — единственный движок, отдающий реальные результаты (заголовки + сниппеты)
- DuckDuckGo блокирует IP капчей, Google даёт 429+CAPTCHA
- Антибот-сайты (Cloudflare и т.п.) не читаются — признать недоступность

## 与其他搜索工具对比

| 工具 | 来源 | 适用场景 |
|-----|------|---------|
| lightpanda (Bing) | lightpanda MCP | 网页搜索/读取 |
| GitHub 搜索 | agent-reach (dev.md) | 仓库/代码搜索 |