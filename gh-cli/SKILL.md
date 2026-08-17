---
name: gh-cli
description: GitHub CLI (gh) comprehensive reference for repositories, issues, pull requests, Actions, projects, releases, gists, codespaces, organizations, extensions, and all GitHub operations from the command line.
---

# GitHub CLI (gh)

Quick reference for GitHub CLI. Load specific section from `references/` as needed.

**Version:** 2.85.0 (current as of January 2026)

## Quick Start

### Authentication
```bash
gh auth login              # Interactive login
gh auth status             # Check status
gh auth setup-git          # Setup git integration
```

### Common Commands
```bash
gh repo create owner/repo  # Create repo
gh issue list              # List issues
gh pr create              # Create PR
gh pr list                # List PRs
gh run list               # List workflow runs
gh api /repos/{owner}/{repo}  # API requests
```

## References

| File | Topic |
|------|-------|
| `references/auth.md` | Authentication (gh auth) |
| `references/config.md` | Configuration (gh config) |
| `references/repo.md` | Repositories (gh repo) |
| `references/issue.md` | Issues (gh issue) |
| `references/pr.md` | Pull Requests (gh pr) |
| `references/actions.md` | Actions (gh run, gh workflow, gh cache) |
| `references/projects.md` | Projects (gh project) |
| `references/releases.md` | Releases (gh release) |
| `references/codespaces.md` | Codespaces (gh codespace) |
| `references/gists.md` | Gists (gh gist) |
| `references/extensions.md` | Extensions (gh extension) |
| `references/search.md` | Search (gh search) |
| `references/secrets.md` | Secrets & Variables (gh secret, gh variable) |
| `references/labels.md` | Labels (gh label) |
| `references/other.md` | Other (gh api, gh alias, gh status, etc.) |

## Examples

```bash
# Clone and setup
gh repo clone owner/repo
cd repo
gh auth setup-git

# Create issue
gh issue create --title "Bug" --body "Description"

# Create PR
gh pr create --title "Fix" --body "Changes"

# List my PRs
gh pr list --author @me

# Merge PR
gh pr merge 123 --squash

# View workflow runs
gh run list --limit 10

# API call
gh api repos/{owner}/{repo}/issues --jq '.[].title'
```

## Official Resources

- Manual: https://cli.github.com/manual/
- GitHub Docs: https://docs.github.com/en/github-cli
- REST API: https://docs.github.com/en/rest
- GraphQL API: https://docs.github.com/en/graphql
