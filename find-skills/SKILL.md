---
name: find-skills
description: |-
  Discover and install agent skills from the open ecosystem. Uses bunx skills CLI.
  Search by keyword, verify quality, install to OpenCode-compatible paths.
  Use proactively when user asks how to do X, find a skill for X, or wants to extend capabilities.

  Examples:
  - user: "find a skill for creative writing" → bunx skills find "creative writing"
  - user: "is there a skill for React testing" → bunx skills find react testing
  - user: "install story-skills" → bunx skills add danjdewhurst/story-skills
  - user: "what skills exist for deployment" → bunx skills find deploy
  - user: "как установить скилл для OpenCode" → clone repo → cp skills/* to .opencode/skills/
---
# Find Skills (OpenCode edition)

Discover and install agent skills from the open ecosystem.

## When to use

- User asks "how do I do X" where X might have an existing skill
- "find a skill for X" / "is there a skill for X"
- "can you do X" where X is a specialized capability
- User wants to extend agent capabilities
- User searches for tools, templates, or workflows

## The Skills CLI

`bunx skills` — package manager for the open agent skills ecosystem.

**Commands:**
- `bunx skills find [query]` — search skills by keyword
- `bunx skills add <package>` — install a skill (places in ~/.agents/skills/)
- `bunx skills check` — check for updates
- `bunx skills update` — update all skills

**Browse:** https://skills.sh/

## Workflow

### 1. Understand the need
Identify: domain (React, writing, design), specific task, whether a skill likely exists.

### 2. Search
```bash
bunx skills find [query]
```
Examples:
- Writing → `bunx skills find writing`
- Fiction → `bunx skills find fiction`
- React testing → `bunx skills find react testing`

### 3. Verify quality
- **Installs:** prefer 1K+. Caution under 100.
- **Source:** official (vercel-labs, anthropics) > unknown
- **GitHub stars:** <100 stars = skeptical

### 4. Present options
Include: name, description, install count, source, install command.

### 5. Install for OpenCode
When user says yes, determine the right method:

**Method A — bunx skills (preferred for standalone skills):**
```bash
bunx skills add <owner/repo> -y
```
Installs to `~/.agents/skills/<name>/`. OpenCode auto-discovers from this path.

**Method B — git clone + copy (for multi-skill repos):**
```bash
git clone <repo-url>
cp -r <repo>/skills/* .opencode/skills/       # project-level
# or
cp -r <repo>/skills/* ~/.config/opencode/skills/  # user-level
```

**Method C — npm global (for complex tools with CLI):**
```bash
npm install -g <package>
```
Only when the skill requires a CLI tool (e.g., novel-writer-skills).

### 6. Verify installation
Check the skill files exist and frontmatter is valid:
```bash
ls ~/.agents/skills/<name>/SKILL.md
head -5 ~/.agents/skills/<name>/SKILL.md
```

## Common categories

| Category | Example queries |
|---|---|
| Writing/Fiction | writing, fiction, novel, creative writing |
| Web Dev | react, nextjs, typescript, css, tailwind |
| Testing | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Documentation | docs, readme, changelog, api-docs |
| Code Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |

## Tips
- Specific keywords work better: "react testing" > "testing"
- Try alternatives: "deploy" → "deployment" → "ci-cd"
- Check popular sources: vercel-labs/agent-skills, anthropics/skills
- For OpenCode: skills in `~/.config/opencode/skills/` are auto-discovered

## When nothing found
1. Acknowledge no existing skill found
2. Offer to help directly
3. Suggest creating a custom skill

## See Also
- **intellisearch** — Поиск JS/TS библиотек, пакетов, GitHub репозиториев
