# gh — Other Commands & Reference

Browse, organizations, status, aliases, API requests, rulesets, attestations, completion, preview, agent tasks, global flags, output formatting, workflows, environment setup, best practices, and help.

---
name: gh-cli
description: GitHub CLI (gh) comprehensive reference for repositories, issues, pull requests, Actions, projects, releases, gists, codespaces, organizations, extensions, and all GitHub operations from the command line.
---

# GitHub CLI (gh)

Comprehensive reference for GitHub CLI (gh) - work seamlessly with GitHub from the command line.

**Version:** 2.85.0 (current as of January 2026)


## CLI Structure

```
gh                          # Root command
├── auth                    # Authentication
│   ├── login
│   ├── logout
│   ├── refresh
│   ├── setup-git
│   ├── status
│   ├── switch
│   └── token
├── browse                  # Open in browser
├── codespace               # GitHub Codespaces
│   ├── code
│   ├── cp
│   ├── create
│   ├── delete
│   ├── edit
│   ├── jupyter
│   ├── list
│   ├── logs
│   ├── ports
│   ├── rebuild
│   ├── ssh
│   ├── stop
│   └── view
├── gist                    # Gists
│   ├── clone
│   ├── create
│   ├── delete
│   ├── edit
│   ├── list
│   ├── rename
│   └── view
├── issue                   # Issues
│   ├── create
│   ├── list
│   ├── status
│   ├── close
│   ├── comment
│   ├── delete
│   ├── develop
│   ├── edit
│   ├── lock
│   ├── pin
│   ├── reopen
│   ├── transfer
│   ├── unlock
│   └── view
├── org                     # Organizations
│   └── list
├── pr                      # Pull Requests
│   ├── create
│   ├── list
│   ├── status
│   ├── checkout
│   ├── checks
│   ├── close
│   ├── comment
│   ├── diff
│   ├── edit
│   ├── lock
│   ├── merge
│   ├── ready
│   ├── reopen
│   ├── revert
│   ├── review
│   ├── unlock
│   ├── update-branch
│   └── view
├── project                 # Projects
│   ├── close
│   ├── copy
│   ├── create
│   ├── delete
│   ├── edit
│   ├── field-create
│   ├── field-delete
│   ├── field-list
│   ├── item-add
│   ├── item-archive
│   ├── item-create
│   ├── item-delete
│   ├── item-edit
│   ├── item-list
│   ├── link
│   ├── list
│   ├── mark-template
│   ├── unlink
│   └── view
├── release                 # Releases
│   ├── create
│   ├── list
│   ├── delete
│   ├── delete-asset
│   ├── download
│   ├── edit
│   ├── upload
│   ├── verify
│   ├── verify-asset
│   └── view
├── repo                    # Repositories
│   ├── create
│   ├── list
│   ├── archive
│   ├── autolink
│   ├── clone
│   ├── delete
│   ├── deploy-key
│   ├── edit
│   ├── fork
│   ├── gitignore
│   ├── license
│   ├── rename
│   ├── set-default
│   ├── sync
│   ├── unarchive
│   └── view
├── cache                   # Actions caches
│   ├── delete
│   └── list
├── run                     # Workflow runs
│   ├── cancel
│   ├── delete
│   ├── download
│   ├── list
│   ├── rerun
│   ├── view
│   └── watch
├── workflow                # Workflows
│   ├── disable
│   ├── enable
│   ├── list
│   ├── run
│   └── view
├── agent-task              # Agent tasks
├── alias                   # Command aliases
│   ├── delete
│   ├── import
│   ├── list
│   └── set
├── api                     # API requests
├── attestation             # Artifact attestations
│   ├── download
│   ├── trusted-root
│   └── verify
├── completion              # Shell completion
├── config                  # Configuration
│   ├── clear-cache
│   ├── get
│   ├── list
│   └── set
├── extension               # Extensions
│   ├── browse
│   ├── create
│   ├── exec
│   ├── install
│   ├── list
│   ├── remove
│   ├── search
│   └── upgrade
├── gpg-key                 # GPG keys
│   ├── add
│   ├── delete
│   └── list
├── label                   # Labels
│   ├── clone
│   ├── create
│   ├── delete
│   ├── edit
│   └── list
├── preview                 # Preview features
├── ruleset                 # Rulesets
│   ├── check
│   ├── list
│   └── view
├── search                  # Search
│   ├── code
│   ├── commits
│   ├── issues
│   ├── prs
│   └── repos
├── secret                  # Secrets
│   ├── delete
│   ├── list
│   └── set
├── ssh-key                 # SSH keys
│   ├── add
│   ├── delete
│   └── list
├── status                  # Status overview
└── variable                # Variables
    ├── delete
    ├── get
    ├── list
    └── set
```


## Browse (gh browse)

```bash
# Open repository in browser
gh browse

# Open specific path
gh browse script/
gh browse main.go:312

# Open issue or PR
gh browse 123

# Open commit
gh browse 77507cd94ccafcf568f8560cfecde965fcfa63

# Open with specific branch
gh browse main.go --branch bug-fix

# Open different repository
gh browse --repo owner/repo

# Open specific pages
gh browse --actions       # Actions tab
gh browse --projects      # Projects tab
gh browse --releases      # Releases tab
gh browse --settings      # Settings page
gh browse --wiki          # Wiki page

# Print URL instead of opening
gh browse --no-browser
```


## Organizations (gh org)

```bash
# List organizations
gh org list

# List for user
gh org list --user username

# JSON output
gh org list --json login,name,description

# View organization
gh org view orgname

# View organization members
gh org view orgname --json members --jq '.members[] | .login'
```


## Status (gh status)

```bash
# Show status overview
gh status

# Status for specific repositories
gh status --repo owner/repo

# JSON output
gh status --json
```


## Aliases (gh alias)

```bash
# List aliases
gh alias list

# Set alias
gh alias set prview 'pr view --web'

# Set shell alias
gh alias set co 'pr checkout' --shell

# Delete alias
gh alias delete prview

# Import aliases
gh alias import ./aliases.sh
```


## API Requests (gh api)

```bash
# Make API request
gh api /user

# Request with method
gh api --method POST /repos/owner/repo/issues \
  --field title="Issue title" \
  --field body="Issue body"

# Request with headers
gh api /user \
  --header "Accept: application/vnd.github.v3+json"

# Request with pagination
gh api /user/repos --paginate

# Raw output (no formatting)
gh api /user --raw

# Include headers in output
gh api /user --include

# Silent mode (no progress output)
gh api /user --silent

# Input from file
gh api --input request.json

# jq query on response
gh api /user --jq '.login'

# Field from response
gh api /repos/owner/repo --jq '.stargazers_count'

# GitHub Enterprise
gh api /user --hostname enterprise.internal

# GraphQL query
gh api graphql \
  -f query='
  {
    viewer {
      login
      repositories(first: 5) {
        nodes {
          name
        }
      }
    }
  }'
```


## Rulesets (gh ruleset)

```bash
# List rulesets
gh ruleset list

# View ruleset
gh ruleset view 123

# Check ruleset
gh ruleset check --branch feature

# Check specific repository
gh ruleset check --repo owner/repo --branch main
```


## Attestations (gh attestation)

```bash
# Download attestation
gh attestation download owner/repo \
  --artifact-id 123456

# Verify attestation
gh attestation verify owner/repo

# Get trusted root
gh attestation trusted-root
```


## Completion (gh completion)

```bash
# Generate shell completion
gh completion -s bash > ~/.gh-complete.bash
gh completion -s zsh > ~/.gh-complete.zsh
gh completion -s fish > ~/.gh-complete.fish
gh completion -s powershell > ~/.gh-complete.ps1

# Shell-specific instructions
gh completion --shell=bash
gh completion --shell=zsh
```


## Preview (gh preview)

```bash
# List preview features
gh preview

# Run preview script
gh preview prompter
```


## Agent Tasks (gh agent-task)

```bash
# List agent tasks
gh agent-task list

# View agent task
gh agent-task view 123

# Create agent task
gh agent-task create --description "My task"
```


## Global Flags

| Flag                       | Description                            |
| -------------------------- | -------------------------------------- |
| `--help` / `-h`            | Show help for command                  |
| `--version`                | Show gh version                        |
| `--repo [HOST/]OWNER/REPO` | Select another repository              |
| `--hostname HOST`          | GitHub hostname                        |
| `--jq EXPRESSION`          | Filter JSON output                     |
| `--json FIELDS`            | Output JSON with specified fields      |
| `--template STRING`        | Format JSON using Go template          |
| `--web`                    | Open in browser                        |
| `--paginate`               | Make additional API calls              |
| `--verbose`                | Show verbose output                    |
| `--debug`                  | Show debug output                      |
| `--timeout SECONDS`        | Maximum API request duration           |
| `--cache CACHE`            | Cache control (default, force, bypass) |


## Output Formatting

### JSON Output

```bash
# Basic JSON
gh repo view --json name,description

# Nested fields
gh repo view --json owner,name --jq '.owner.login + "/" + .name'

# Array operations
gh pr list --json number,title --jq '.[] | select(.number > 100)'

# Complex queries
gh issue list --json number,title,labels \
  --jq '.[] | {number, title: .title, tags: [.labels[].name]}'
```

### Template Output

```bash
# Custom template
gh repo view \
  --template '{{.name}}: {{.description}}'

# Multiline template
gh pr view 123 \
  --template 'Title: {{.title}}
Author: {{.author.login}}
State: {{.state}}
'
```


## Common Workflows

### Create PR from Issue

```bash
# Create branch from issue
gh issue develop 123 --branch feature/issue-123

# Make changes, commit, push
git add .
git commit -m "Fix issue #123"
git push

# Create PR linking to issue
gh pr create --title "Fix #123" --body "Closes #123"
```

### Bulk Operations

```bash
# Close multiple issues
gh issue list --search "label:stale" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue close {} --comment "Closing as stale"

# Add label to multiple PRs
gh pr list --search "review:required" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh pr edit {} --add-label needs-review
```

### Repository Setup Workflow

```bash
# Create repository with initial setup
gh repo create my-project --public \
  --description "My awesome project" \
  --clone \
  --gitignore python \
  --license mit

cd my-project

# Set up branches
git checkout -b develop
git push -u origin develop

# Create labels
gh label create bug --color "d73a4a" --description "Bug report"
gh label create enhancement --color "a2eeef" --description "Feature request"
gh label create documentation --color "0075ca" --description "Documentation"
```

### CI/CD Workflow

```bash
# Run workflow and wait
RUN_ID=$(gh workflow run ci.yml --ref main --jq '.databaseId')

# Watch the run
gh run watch "$RUN_ID"

# Download artifacts on completion
gh run download "$RUN_ID" --dir ./artifacts
```

### Fork Sync Workflow

```bash
# Fork repository
gh repo fork original/repo --clone

cd repo

# Add upstream remote
git remote add upstream https://github.com/original/repo.git

# Sync fork
gh repo sync

# Or manual sync
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```


## Environment Setup

### Shell Integration

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(gh completion -s bash)"  # or zsh/fish

# Create useful aliases
alias gs='gh status'
alias gpr='gh pr view --web'
alias gir='gh issue view --web'
alias gco='gh pr checkout'
```

### Git Configuration

```bash
# Use gh as credential helper
gh auth setup-git

# Set gh as default for repo operations
git config --global credential.helper 'gh !gh auth setup-git'

# Or manually
git config --global credential.helper github
```


## Best Practices

1. **Authentication**: Use environment variables for automation

   ```bash
   export GH_TOKEN=$(gh auth token)
   ```

2. **Default Repository**: Set default to avoid repetition

   ```bash
   gh repo set-default owner/repo
   ```

3. **JSON Parsing**: Use jq for complex data extraction

   ```bash
   gh pr list --json number,title --jq '.[] | select(.title | contains("fix"))'
   ```

4. **Pagination**: Use --paginate for large result sets

   ```bash
   gh issue list --state all --paginate
   ```

5. **Caching**: Use cache control for frequently accessed data
   ```bash
   gh api /user --cache force
   ```


## Getting Help

```bash
# General help
gh --help

# Command help
gh pr --help
gh issue create --help

# Help topics
gh help formatting
gh help environment
gh help exit-codes
gh help accessibility
```


## References

- Official Manual: https://cli.github.com/manual/
- GitHub Docs: https://docs.github.com/en/github-cli
- REST API: https://docs.github.com/en/rest
- GraphQL API: https://docs.github.com/en/graphql
