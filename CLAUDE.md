# CLAUDE.md

## Project Overview

This is an autonomous QA testing agent that browses websites using Playwright, identifies bugs and feature opportunities, and files them as GitHub issues using the Claude API.

## Architecture

```
main.py           → CLI entry point, orchestrates everything
agent.py          → Claude API tool-use loop (the "brain")
browser.py        → Playwright browser controller
github_reporter.py → GitHub issue creation with duplicate detection
config.py         → Environment variable loading
```

## Key Commands

```bash
# Activate venv
source .venv/bin/activate

# Dry run (no issues created)
python main.py --dry-run --max-steps 10

# Full run
python main.py --max-steps 20

# Focus on specific feature
python main.py --focus "add part" --max-steps 15

# Headless mode (no browser window)
python main.py --headless
```

## Environment Variables

Required in `.env`:
- `ANTHROPIC_API_KEY` - Claude API key
- `CRANKCASE_URL` - Target website URL
- `CRANKCASE_USERNAME` - Test account username
- `CRANKCASE_PASSWORD` - Test account password
- `GITHUB_TOKEN` - GitHub token with repo scope
- `GITHUB_REPO` - Target repo for issues (e.g., `owner/repo`)

## How the Agent Works

1. Browser navigates to target site
2. Claude decides what to test next (via tool use)
3. Agent executes browser actions (click, fill, navigate)
4. Claude analyzes results and identifies issues
5. Bugs/features are filed to GitHub with duplicate detection
6. Loop continues until max steps or Claude calls `finish`

## Modifying Behavior

- **System prompt**: Edit `SYSTEM_PROMPT` in `agent.py` to change testing strategy
- **Tools**: Edit `TOOLS` list in `agent.py` to add/modify capabilities
- **Login flow**: Edit `login()` in `browser.py` for site-specific auth
- **Issue format**: Edit `create_bug()`/`create_feature_request()` in `github_reporter.py`
