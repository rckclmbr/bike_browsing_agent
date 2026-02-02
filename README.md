# Bike Browsing Agent

An autonomous QA testing agent that browses your website like a real user, finds bugs and UX issues, and automatically files them as GitHub issues.

Built with Claude API + Playwright.

## Features

- **Autonomous exploration** - Claude decides what to test, no scripts needed
- **Real browser testing** - Uses Playwright to interact with your site like a user
- **Automatic issue filing** - Bugs and feature requests go straight to GitHub
- **Duplicate detection** - Won't file the same issue twice
- **Dry run mode** - Test without creating real issues
- **Focused testing** - Target specific features with `--focus`

## Quick Start

```bash
# Clone and setup
git clone https://github.com/rckclmbr/bike_browsing_agent.git
cd bike_browsing_agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python main.py --dry-run --max-steps 10
```

## Configuration

Create a `.env` file with:

```env
ANTHROPIC_API_KEY=sk-ant-...
CRANKCASE_URL=https://your-site.com
CRANKCASE_USERNAME=test@example.com
CRANKCASE_PASSWORD=testpass123
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo
```

## Usage

```bash
# Dry run - see what issues would be created
python main.py --dry-run

# Full run - creates real GitHub issues
python main.py --max-steps 20

# Focus on specific feature
python main.py --focus "login flow"

# Run headless (no browser window)
python main.py --headless

# Combine options
python main.py --headless --max-steps 30 --focus "checkout"
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--max-steps N` | Maximum actions before stopping (default: 100) |
| `--headless` | Run browser without visible window |
| `--dry-run` | Find issues but don't create GitHub issues |
| `--focus TEXT` | Focus testing on a specific feature |

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                         Agent                           │
│                                                         │
│  Claude API decides:        Playwright executes:        │
│  - What to click            - Browser navigation        │
│  - What to test             - Form filling              │
│  - When something's a bug   - Screenshots               │
│  - When to stop             - Element interaction       │
│                                                         │
│              GitHub API files issues                    │
└─────────────────────────────────────────────────────────┘
```

1. Agent loads your website in a real browser
2. Claude sees the page structure and decides what to test
3. Agent executes Claude's actions (click, type, navigate)
4. Claude analyzes results - looking for bugs, errors, UX issues
5. Issues are filed to GitHub with steps to reproduce
6. Process repeats until done or max steps reached

## Customization

### Testing Strategy

Edit `SYSTEM_PROMPT` in `agent.py` to change how Claude approaches testing:

```python
SYSTEM_PROMPT = """You are a thorough QA tester...
# Add your custom instructions here
"""
```

### Login Flow

The default login looks for email/password fields. For custom auth (OAuth, SSO, etc.), edit `login()` in `browser.py`.

### Issue Format

Modify `create_bug()` and `create_feature_request()` in `github_reporter.py` to change issue templates.

## Requirements

- Python 3.10+
- Anthropic API key
- GitHub token with `repo` scope
- System dependencies for Playwright (see [Playwright docs](https://playwright.dev/python/docs/intro))

## License

MIT
