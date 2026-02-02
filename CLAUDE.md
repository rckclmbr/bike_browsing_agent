# CLAUDE.md

## Project Overview

This is an autonomous QA testing agent that browses websites using Playwright, identifies bugs and feature opportunities, and files them as GitHub issues. It uses Claude CLI with an MCP server for the AI loop.

## Architecture

```
run.sh            → Invokes Claude CLI with prompt
browser_mcp.py    → MCP server exposing browser/GitHub tools
browser.py        → Playwright browser controller
github_reporter.py → GitHub issue creation with duplicate detection
config.py         → Environment variable loading
```

## Key Commands

```bash
# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Dry run (no issues created)
DRY_RUN=true ./run.sh 10

# Full run (20 turns default)
./run.sh

# Custom turns
./run.sh 30

# Focus on specific feature
./run.sh 15 "add part"

# Headless mode (no browser window)
HEADLESS=true ./run.sh
```

## Environment Variables

Required in `.env`:
- `CRANKCASE_URL` - Target website URL
- `GITHUB_TOKEN` - GitHub token with repo scope
- `GITHUB_REPO` - Target repo for issues (e.g., `owner/repo`)
- `JWT_SECRET` - JWT secret for session cookie injection
- `SESSION_USER_ID` - User ID for JWT payload
- `SESSION_USER_NAME` - Username for JWT payload

Optional:
- `DRY_RUN` - Set to "true" to skip issue creation
- `HEADLESS` - Set to "true" for headless browser
- `MAX_ISSUES` - Max issues to create per session (default: 10)

Note: Claude CLI handles its own authentication - no `ANTHROPIC_API_KEY` needed.

## How the Agent Works

1. `run.sh` invokes Claude CLI with the MCP server and system prompt
2. Claude calls `start_browser` to launch Playwright and log in
3. Claude uses `get_page_state`, `click`, `fill`, etc. to explore the app
4. Claude calls `report_bug` or `report_feature_request` for issues found
5. Claude calls `stop_browser` when done and summarizes findings
6. Claude CLI shows token usage at the end

## Modifying Behavior

- **System prompt**: Edit the `PROMPT` variable in `run.sh`
- **Tools**: Edit tool functions in `browser_mcp.py`
- **Login flow**: Edit `login()` in `browser.py` for site-specific auth
- **Issue format**: Edit `create_bug()`/`create_feature_request()` in `github_reporter.py`
