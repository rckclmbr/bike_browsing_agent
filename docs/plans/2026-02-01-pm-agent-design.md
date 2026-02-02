# PM Agent Design

## Overview

A product manager agent that explores the app, proposes strategic directions, and creates actionable GitHub issues for other agents to implement.

## Architecture

```
pm_mcp.py    → MCP server (browser + GitHub tools)
pm.sh        → Two-phase wrapper script
docs/strategy/ → Strategy docs written by PM
```

## Tools

**Browser (reused from QA):**
- `start_browser(headless)` - Launch browser and login
- `stop_browser()` - Close browser
- `get_page_state()` - Get current page HTML
- `navigate(url)` - Go to URL
- `click(selector)` - Click element

**GitHub (new):**
- `list_issues(state, labels)` - List issues via gh CLI
- `list_prs(state)` - List PRs
- `get_issue(number)` - Get issue details
- `create_issue(title, body, labels)` - Create issue

**Strategy (new):**
- `save_strategy(filename, content)` - Write to docs/strategy/

## Workflow

### Phase 1: Explore
```bash
./pm.sh explore
```
1. PM browses app, understands features
2. PM reads GitHub issues, understands current work
3. PM writes proposals to `docs/strategy/proposals.md`
4. PM stops browser

### Phase 2: Execute
```bash
./pm.sh execute "Premium Analytics Tier"
```
1. PM reads proposals doc for context
2. PM writes full strategy to `docs/strategy/YYYY-MM-DD-{topic}.md`
3. PM creates 5-10 GitHub issues referencing the strategy
4. Each issue is small, actionable, has acceptance criteria

## Issue Format

```markdown
## Context
Part of [Strategy Name](../docs/strategy/2026-02-01-strategy.md)

## Task
Description of what to build...

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```
