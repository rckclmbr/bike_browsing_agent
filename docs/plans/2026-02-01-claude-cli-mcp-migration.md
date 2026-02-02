# Claude CLI + MCP Migration

## Goal

Replace Anthropic API calls with Claude CLI to get:
- Simpler auth (use CLI's built-in auth)
- Cost visibility (token usage shown automatically)

## Architecture

### Before
```
main.py → agent.py (Anthropic API loop) → browser.py
                                        → github_reporter.py
```

### After
```
run.sh → claude CLI → browser_mcp.py (MCP server)
                    → github_reporter.py (called from MCP server)
```

## Files

| File | Action |
|------|--------|
| `browser_mcp.py` | Create - MCP server with browser/GitHub tools |
| `run.sh` | Create - Wrapper script to invoke Claude CLI |
| `agent.py` | Delete - replaced by Claude CLI |
| `main.py` | Delete - replaced by run.sh |
| `browser.py` | Keep - unchanged |
| `github_reporter.py` | Keep - unchanged |
| `config.py` | Keep - still needed for env vars |

## MCP Server Design

Tools exposed:
- `start_browser(headless: bool)` - Start browser and login
- `stop_browser()` - Close browser
- `get_page_state()` - Get URL, title, simplified HTML
- `navigate(url: str)` - Go to URL
- `click(selector: str)` - Click element
- `fill(selector: str, text: str)` - Fill input
- `select(selector: str, value: str)` - Select dropdown option
- `screenshot()` - Take screenshot
- `report_bug(title, description, steps_to_reproduce)` - Create GitHub issue
- `report_feature_request(title, description, rationale)` - Create GitHub issue

Global state holds `BrowserController` and `GitHubReporter` instances.

## Run Script

```bash
./run.sh              # Default 20 turns
./run.sh 10           # 10 turns max
./run.sh 15 "add part"  # Focus on feature
```

Flags:
- `--dry-run` via env var to skip issue creation
- `--headless` passed to start_browser tool

## Dependencies

Add to requirements.txt:
```
fastmcp
```
