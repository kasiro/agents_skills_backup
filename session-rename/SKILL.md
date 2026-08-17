---
name: session-rename
description: |-
  Batch rename OpenCode sessions with default titles ("New session - ...") using AI-generated titles.
  Queries SQLite DB for default-titled parent sessions, generates titles via OpenCode's built-in `title` agent,
  and updates via HTTP API. Use proactively when: session list is cluttered with default names,
  user asks to clean up/rename sessions, or session history is unusable due to generic titles.

  Examples:
  - user: "Переименуй сессии с дефолтными названиями" → run batch-rename-sessions.ts
  - user: "Почисти список сессий" → run batch-rename-sessions.ts with dry-run first
  - user: "У меня сессии все 'New session - ...'" → run batch-rename-sessions.ts
  - user: "Переименуй 5 сессий" → MAX_SESSIONS=5 npx tsx batch-rename-sessions.ts
---

# Session Batch Rename

Batch rename OpenCode sessions that still have default titles ("New session - <timestamp>") using AI-generated titles.

## How It Works

1. Queries OpenCode SQLite DB for parent sessions with default titles
2. For each session, fetches messages via HTTP API
3. Extracts first non-synthetic user message as context
4. Creates a temporary worker session and invokes the built-in `title` agent
5. Updates session title via `PATCH /session/{id}`
6. Cleans up the worker session

## Prerequisites

- OpenCode server running (`opencode serve --port 4096`)
- `sqlite3` on PATH
- `npx tsx` or `bun` to run TypeScript

## Usage

```bash
# Dry-run on 5 sessions
MAX_SESSIONS=5 npx tsx scripts/batch-rename-sessions.ts

# Rename all default-titled sessions
npx tsx scripts/batch-rename-sessions.ts
```

## Configuration (environment variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCODE_URL` | `http://127.0.0.1:4096` | OpenCode server URL |
| `OPENCODE_PROVIDER` | `anthropic` | Provider ID for title model |
| `OPENCODE_MODEL` | `claude-haiku-4-5` | Model ID for title generation |
| `OPENCODE_DB` | `~/.local/share/opencode/opencode.db` | SQLite DB path |
| `MAX_SESSIONS` | `0` (all) | Limit sessions to process |
| `REQUEST_DELAY` | `1200` | Delay in ms between requests |

## Custom Provider Examples

```bash
# OpenAI
OPENCODE_PROVIDER=openai OPENCODE_MODEL=gpt-4o-mini npx tsx scripts/batch-rename-sessions.ts

# Custom port
OPENCODE_URL=http://127.0.0.1:8080 npx tsx scripts/batch-rename-sessions.ts
```

## Output

Sessions with no user content are skipped. At the end, a summary shows renamed/skipped/failed counts.
