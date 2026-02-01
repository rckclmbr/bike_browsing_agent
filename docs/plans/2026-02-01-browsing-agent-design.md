# CrankCase Browsing Agent Design

## Overview

Autonomous Python agent that browses the CrankCase bike maintenance app, tests it like a real user, and reports bugs/feature requests as GitHub issues.

## Target

- **Site**: https://bikedbmcpserver-production.up.railway.app/
- **GitHub Repo**: rckclmbr/bike_db_mcp_server

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Runner                         │
│                   (main.py)                             │
│                                                         │
│  1. Launches browser with Playwright                    │
│  2. Logs into CrankCase                                 │
│  3. Runs exploration/testing loop with Claude           │
│  4. Creates GitHub issues for findings                  │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Playwright    │  │   Claude API    │  │   GitHub API    │
│                 │  │                 │  │                 │
│ - Navigate      │  │ - Decide what   │  │ - Create issues │
│ - Click/type    │  │   to test next  │  │ - Check for     │
│ - Screenshot    │  │ - Identify bugs │  │   duplicates    │
│ - Get page HTML │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Core loop:**
1. Claude sees the current page state (HTML/screenshot)
2. Claude decides: explore more, test something, or report a finding
3. Agent executes Claude's chosen action via Playwright
4. Repeat until Claude decides it's done or hits a limit

## Files

```
bike_browsing_agent/
├── main.py              # Entry point, CLI
├── agent.py             # Claude API + tool loop
├── browser.py           # Playwright wrapper
├── github_reporter.py   # GitHub issue creation
├── config.py            # Load env vars
├── requirements.txt     # Dependencies
└── .env.example         # Template for credentials
```

## Browser Tools

**Navigation & Observation:**
- `navigate(url)` - Go to a URL
- `get_page_state()` - Returns current URL, page title, and simplified HTML
- `screenshot()` - Take a screenshot for visual inspection (used sparingly)

**Interaction:**
- `click(selector)` - Click an element
- `fill(selector, text)` - Type into an input field
- `select(selector, value)` - Choose from a dropdown

**Reporting:**
- `report_bug(title, description, steps_to_reproduce)` - Creates GitHub issue labeled "bug"
- `report_feature_request(title, description, rationale)` - Creates GitHub issue labeled "enhancement"
- `finish(summary)` - End the session

**Design decisions:**
- Simplified HTML over raw HTML to reduce tokens
- CSS selectors for element targeting
- Screenshots used sparingly (vision tokens are expensive)

## Agent Behavior

**System prompt persona:** Thorough QA tester for a bike maintenance app.

**Testing strategy:**
1. Explore first - Navigate through main features
2. Test happy paths - Main workflows (add part, log service, etc.)
3. Test edge cases - Empty inputs, special characters, long text
4. Test error handling - What happens when things go wrong
5. Note UX friction - Confusing labels, missing feedback

**Bug criteria:**
- Something is broken (error, crash, wrong behavior)
- Data isn't saved/displayed correctly
- UI is unresponsive or shows wrong state

**Feature request criteria:**
- Missing functionality users would expect
- UX improvements

**Duplicate prevention:**
- Fetch open issues before creating
- Claude checks for similar existing issues
- Skip or comment instead of duplicating

## Configuration

Environment variables (`.env`):
```
ANTHROPIC_API_KEY=sk-ant-...
CRANKCASE_URL=https://bikedbmcpserver-production.up.railway.app
CRANKCASE_USERNAME=testuser@example.com
CRANKCASE_PASSWORD=testpassword123
GITHUB_TOKEN=ghp_...
GITHUB_REPO=rckclmbr/bike_db_mcp_server
```

## CLI

```bash
python main.py                       # Default run
python main.py --max-steps 50        # Limit actions
python main.py --focus "add part"    # Focus on specific feature
python main.py --headless            # No visible browser
python main.py --dry-run             # Find bugs but don't create issues
```

## Safety Limits

- Max steps: 100 (default)
- Max issues per run: 10 (default)
- Timeout per action: 30 seconds
