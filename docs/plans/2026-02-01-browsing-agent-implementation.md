# CrankCase Browsing Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an autonomous Python agent that tests the CrankCase bike maintenance app and reports bugs/features to GitHub Issues.

**Architecture:** Playwright controls a browser, Claude API decides actions via tool use, GitHub API creates issues. A main loop orchestrates the flow.

**Tech Stack:** Python 3.11+, anthropic SDK, playwright, PyGithub, python-dotenv

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```txt
anthropic>=0.39.0
playwright>=1.40.0
PyGithub>=2.1.0
python-dotenv>=1.0.0
```

**Step 2: Create .env.example**

```txt
ANTHROPIC_API_KEY=sk-ant-...
CRANKCASE_URL=https://bikedbmcpserver-production.up.railway.app
CRANKCASE_USERNAME=your-test-email@example.com
CRANKCASE_PASSWORD=your-test-password
GITHUB_TOKEN=ghp_...
GITHUB_REPO=rckclmbr/bike_db_mcp_server
```

**Step 3: Create .gitignore**

```txt
.env
__pycache__/
*.pyc
.venv/
venv/
screenshots/
```

**Step 4: Install dependencies**

Run: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && playwright install chromium`

Expected: Dependencies installed, chromium browser downloaded

**Step 5: Commit**

```bash
git add requirements.txt .env.example .gitignore
git commit -m "chore: add project setup files"
```

---

### Task 2: Configuration Module

**Files:**
- Create: `config.py`

**Step 1: Create config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
    CRANKCASE_URL: str = os.environ["CRANKCASE_URL"]
    CRANKCASE_USERNAME: str = os.environ["CRANKCASE_USERNAME"]
    CRANKCASE_PASSWORD: str = os.environ["CRANKCASE_PASSWORD"]
    GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
    GITHUB_REPO: str = os.environ["GITHUB_REPO"]

    # Defaults
    MAX_STEPS: int = int(os.environ.get("MAX_STEPS", "100"))
    MAX_ISSUES: int = int(os.environ.get("MAX_ISSUES", "10"))
    ACTION_TIMEOUT: int = int(os.environ.get("ACTION_TIMEOUT", "30000"))  # ms


config = Config()
```

**Step 2: Verify it loads (manual test)**

Create a `.env` file with your actual credentials, then run:
```bash
python -c "from config import config; print(config.CRANKCASE_URL)"
```

Expected: Prints `https://bikedbmcpserver-production.up.railway.app`

**Step 3: Commit**

```bash
git add config.py
git commit -m "feat: add configuration module"
```

---

### Task 3: Browser Module

**Files:**
- Create: `browser.py`

**Step 1: Create browser.py with core browser control**

```python
from playwright.sync_api import sync_playwright, Page, Browser
from config import config
import re


class BrowserController:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(config.ACTION_TIMEOUT)

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate(self, url: str) -> dict:
        self.page.goto(url)
        return {"status": "ok", "url": self.page.url}

    def click(self, selector: str) -> dict:
        try:
            self.page.click(selector, timeout=config.ACTION_TIMEOUT)
            self.page.wait_for_load_state("networkidle", timeout=5000)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fill(self, selector: str, text: str) -> dict:
        try:
            self.page.fill(selector, text)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def select(self, selector: str, value: str) -> dict:
        try:
            self.page.select_option(selector, value)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def screenshot(self, path: str = "screenshot.png") -> dict:
        self.page.screenshot(path=path)
        return {"status": "ok", "path": path}

    def get_page_state(self) -> dict:
        url = self.page.url
        title = self.page.title()
        html = self._get_simplified_html()
        return {
            "url": url,
            "title": title,
            "html": html,
        }

    def _get_simplified_html(self) -> str:
        """Extract simplified HTML with interactive elements and text."""
        script = """
        () => {
            const elements = [];

            // Get all interactive and content elements
            const selectors = 'a, button, input, select, textarea, form, h1, h2, h3, h4, label, [role="button"], [onclick]';
            document.querySelectorAll(selectors).forEach((el, idx) => {
                const tag = el.tagName.toLowerCase();
                const text = el.innerText?.slice(0, 100) || '';
                const attrs = [];

                if (el.id) attrs.push(`id="${el.id}"`);
                if (el.name) attrs.push(`name="${el.name}"`);
                if (el.className) attrs.push(`class="${el.className}"`);
                if (el.type) attrs.push(`type="${el.type}"`);
                if (el.href) attrs.push(`href="${el.href}"`);
                if (el.placeholder) attrs.push(`placeholder="${el.placeholder}"`);
                if (el.value && tag === 'input') attrs.push(`value="${el.value}"`);

                const attrStr = attrs.length ? ' ' + attrs.join(' ') : '';
                elements.push(`<${tag}${attrStr}>${text.trim()}</${tag}>`);
            });

            return elements.join('\\n');
        }
        """
        return self.page.evaluate(script)

    def login(self, username: str, password: str) -> dict:
        """Attempt to log in - this is site-specific and may need adjustment."""
        try:
            # Navigate to the site first
            self.navigate(config.CRANKCASE_URL)

            # Look for common login patterns
            # This may need customization based on CrankCase's actual login flow
            self.page.wait_for_load_state("networkidle")

            # Try to find and fill login form
            if self.page.locator('input[type="email"], input[name="email"]').count() > 0:
                self.page.fill('input[type="email"], input[name="email"]', username)
            if self.page.locator('input[type="password"]').count() > 0:
                self.page.fill('input[type="password"]', password)

            # Click submit button
            if self.page.locator('button[type="submit"]').count() > 0:
                self.page.click('button[type="submit"]')
                self.page.wait_for_load_state("networkidle")

            return {"status": "ok", "url": self.page.url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

**Step 2: Manual test browser module**

Run:
```bash
python -c "
from browser import BrowserController
bc = BrowserController(headless=False)
bc.start()
bc.navigate('https://bikedbmcpserver-production.up.railway.app')
print(bc.get_page_state())
bc.stop()
"
```

Expected: Browser opens, navigates to site, prints page state, closes.

**Step 3: Commit**

```bash
git add browser.py
git commit -m "feat: add browser controller with Playwright"
```

---

### Task 4: GitHub Reporter Module

**Files:**
- Create: `github_reporter.py`

**Step 1: Create github_reporter.py**

```python
from github import Github
from config import config


class GitHubReporter:
    def __init__(self):
        self.github = Github(config.GITHUB_TOKEN)
        self.repo = self.github.get_repo(config.GITHUB_REPO)
        self._existing_issues: list[str] | None = None

    def get_existing_issues(self) -> list[str]:
        """Fetch titles of open issues for duplicate detection."""
        if self._existing_issues is None:
            issues = self.repo.get_issues(state="open")
            self._existing_issues = [issue.title.lower() for issue in issues]
        return self._existing_issues

    def is_duplicate(self, title: str) -> bool:
        """Check if a similar issue already exists."""
        existing = self.get_existing_issues()
        title_lower = title.lower()
        for existing_title in existing:
            # Simple similarity check - title contains or is contained
            if title_lower in existing_title or existing_title in title_lower:
                return True
        return False

    def create_bug(self, title: str, description: str, steps_to_reproduce: str) -> dict:
        """Create a bug issue."""
        if self.is_duplicate(title):
            return {"status": "skipped", "reason": "duplicate"}

        body = f"""## Description
{description}

## Steps to Reproduce
{steps_to_reproduce}

---
*Reported by automated QA agent*
"""
        issue = self.repo.create_issue(title=title, body=body, labels=["bug"])
        self._existing_issues.append(title.lower())
        return {"status": "created", "url": issue.html_url, "number": issue.number}

    def create_feature_request(self, title: str, description: str, rationale: str) -> dict:
        """Create a feature request issue."""
        if self.is_duplicate(title):
            return {"status": "skipped", "reason": "duplicate"}

        body = f"""## Description
{description}

## Rationale
{rationale}

---
*Suggested by automated QA agent*
"""
        issue = self.repo.create_issue(title=title, body=body, labels=["enhancement"])
        self._existing_issues.append(title.lower())
        return {"status": "created", "url": issue.html_url, "number": issue.number}
```

**Step 2: Manual test (dry run)**

Run:
```bash
python -c "
from github_reporter import GitHubReporter
gr = GitHubReporter()
print('Existing issues:', gr.get_existing_issues()[:5])
print('Is duplicate \"test\":', gr.is_duplicate('test'))
"
```

Expected: Prints list of existing issue titles, duplicate check result.

**Step 3: Commit**

```bash
git add github_reporter.py
git commit -m "feat: add GitHub reporter for creating issues"
```

---

### Task 5: Agent Module with Claude Tool Use

**Files:**
- Create: `agent.py`

**Step 1: Create agent.py with tool definitions**

```python
import anthropic
import json
import base64
from config import config
from browser import BrowserController
from github_reporter import GitHubReporter

TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate to a URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to navigate to"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_page_state",
        "description": "Get the current page URL, title, and simplified HTML showing interactive elements",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "click",
        "description": "Click on an element using a CSS selector",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for the element to click"}
            },
            "required": ["selector"]
        }
    },
    {
        "name": "fill",
        "description": "Fill a text input field",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for the input field"},
                "text": {"type": "string", "description": "Text to enter"}
            },
            "required": ["selector", "text"]
        }
    },
    {
        "name": "select",
        "description": "Select an option from a dropdown",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for the select element"},
                "value": {"type": "string", "description": "Value to select"}
            },
            "required": ["selector", "value"]
        }
    },
    {
        "name": "screenshot",
        "description": "Take a screenshot of the current page. Use sparingly - only when you suspect a visual bug.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "report_bug",
        "description": "Report a bug found during testing",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short descriptive title for the bug"},
                "description": {"type": "string", "description": "Detailed description of the bug"},
                "steps_to_reproduce": {"type": "string", "description": "Step-by-step instructions to reproduce the bug"}
            },
            "required": ["title", "description", "steps_to_reproduce"]
        }
    },
    {
        "name": "report_feature_request",
        "description": "Suggest a feature or improvement",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short descriptive title for the feature"},
                "description": {"type": "string", "description": "What the feature should do"},
                "rationale": {"type": "string", "description": "Why this feature would be valuable"}
            },
            "required": ["title", "description", "rationale"]
        }
    },
    {
        "name": "finish",
        "description": "End the testing session",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Summary of what was tested and found"}
            },
            "required": ["summary"]
        }
    }
]

SYSTEM_PROMPT = """You are a thorough QA tester for CrankCase, a bike maintenance tracking application.

Your job is to:
1. Explore the application like a real user would
2. Test the main features and workflows
3. Look for bugs, errors, and UX issues
4. Suggest improvements and missing features

Testing strategy:
- Start by getting the page state to see what's on the current page
- Explore the main navigation and features
- Test happy paths first (normal usage)
- Then test edge cases (empty inputs, special characters, long text)
- Look for error handling issues
- Note confusing UX or missing feedback

What qualifies as a bug:
- Errors, crashes, or unexpected behavior
- Data not saved or displayed correctly
- UI not responding or showing wrong state
- Broken links or missing pages

What qualifies as a feature request:
- Missing functionality users would expect
- UX improvements (better labels, confirmations, feedback)
- Helpful features that don't exist

Be specific in your reports - include exact steps to reproduce bugs.
Use screenshots only when you suspect a visual/layout issue.

When you've tested enough or hit repeated issues, use the finish tool."""


class Agent:
    def __init__(self, browser: BrowserController, reporter: GitHubReporter, dry_run: bool = False):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.browser = browser
        self.reporter = reporter
        self.dry_run = dry_run
        self.messages: list = []
        self.step_count = 0
        self.issues_created = 0
        self.finished = False
        self.summary = ""

    def _execute_tool(self, name: str, args: dict) -> str:
        """Execute a tool and return the result as a string."""
        print(f"  -> Tool: {name}({args})")

        if name == "navigate":
            result = self.browser.navigate(args["url"])
        elif name == "get_page_state":
            result = self.browser.get_page_state()
        elif name == "click":
            result = self.browser.click(args["selector"])
        elif name == "fill":
            result = self.browser.fill(args["selector"], args["text"])
        elif name == "select":
            result = self.browser.select(args["selector"], args["value"])
        elif name == "screenshot":
            path = f"screenshots/step_{self.step_count}.png"
            import os
            os.makedirs("screenshots", exist_ok=True)
            result = self.browser.screenshot(path)
            # For screenshots, we'd need to return image data for Claude to see
            # For now, just confirm it was taken
            result["note"] = "Screenshot saved. Describe what you expected to see."
        elif name == "report_bug":
            if self.dry_run:
                result = {"status": "dry_run", "would_create": "bug", "title": args["title"]}
                print(f"  [DRY RUN] Would create bug: {args['title']}")
            elif self.issues_created >= config.MAX_ISSUES:
                result = {"status": "skipped", "reason": "max issues reached"}
            else:
                result = self.reporter.create_bug(
                    args["title"], args["description"], args["steps_to_reproduce"]
                )
                if result["status"] == "created":
                    self.issues_created += 1
                    print(f"  Created bug #{result['number']}: {args['title']}")
        elif name == "report_feature_request":
            if self.dry_run:
                result = {"status": "dry_run", "would_create": "feature", "title": args["title"]}
                print(f"  [DRY RUN] Would create feature request: {args['title']}")
            elif self.issues_created >= config.MAX_ISSUES:
                result = {"status": "skipped", "reason": "max issues reached"}
            else:
                result = self.reporter.create_feature_request(
                    args["title"], args["description"], args["rationale"]
                )
                if result["status"] == "created":
                    self.issues_created += 1
                    print(f"  Created feature #{result['number']}: {args['title']}")
        elif name == "finish":
            self.finished = True
            self.summary = args["summary"]
            result = {"status": "ok", "message": "Session ended"}
        else:
            result = {"error": f"Unknown tool: {name}"}

        return json.dumps(result)

    def run_step(self) -> bool:
        """Run one step of the agent loop. Returns False if finished."""
        if self.finished:
            return False

        self.step_count += 1
        print(f"\n=== Step {self.step_count} ===")

        # Call Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=self.messages if self.messages else [
                {"role": "user", "content": "Begin testing the application. Start by getting the page state to see what's on screen."}
            ]
        )

        # Process response
        assistant_content = []
        tool_results = []

        for block in response.content:
            if block.type == "text":
                print(f"Claude: {block.text}")
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
                result = self._execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Update message history
        self.messages.append({"role": "assistant", "content": assistant_content})
        if tool_results:
            self.messages.append({"role": "user", "content": tool_results})

        # Check stop conditions
        if self.finished:
            return False
        if response.stop_reason == "end_turn" and not any(b.type == "tool_use" for b in response.content):
            return False

        return True

    def run(self, max_steps: int | None = None) -> str:
        """Run the agent until finished or max steps reached."""
        max_steps = max_steps or config.MAX_STEPS

        while self.step_count < max_steps:
            if not self.run_step():
                break

        if not self.finished:
            self.summary = f"Session ended after {self.step_count} steps (limit reached)"

        return self.summary
```

**Step 2: Commit**

```bash
git add agent.py
git commit -m "feat: add agent with Claude tool use"
```

---

### Task 6: Main Entry Point

**Files:**
- Create: `main.py`

**Step 1: Create main.py with CLI**

```python
import argparse
from browser import BrowserController
from github_reporter import GitHubReporter
from agent import Agent
from config import config


def main():
    parser = argparse.ArgumentParser(description="CrankCase QA Testing Agent")
    parser.add_argument("--max-steps", type=int, default=config.MAX_STEPS, help="Maximum number of steps")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--dry-run", action="store_true", help="Don't create GitHub issues")
    parser.add_argument("--focus", type=str, help="Focus testing on a specific feature")
    args = parser.parse_args()

    print("=" * 50)
    print("CrankCase QA Testing Agent")
    print("=" * 50)
    print(f"Target: {config.CRANKCASE_URL}")
    print(f"Max steps: {args.max_steps}")
    print(f"Headless: {args.headless}")
    print(f"Dry run: {args.dry_run}")
    if args.focus:
        print(f"Focus: {args.focus}")
    print("=" * 50)

    # Initialize components
    browser = BrowserController(headless=args.headless)
    reporter = GitHubReporter()

    try:
        # Start browser and login
        print("\nStarting browser...")
        browser.start()

        print("Logging in...")
        login_result = browser.login(config.CRANKCASE_USERNAME, config.CRANKCASE_PASSWORD)
        if login_result["status"] == "error":
            print(f"Login failed: {login_result['message']}")
            print("Continuing anyway - site may not require login")

        # Create and run agent
        agent = Agent(browser, reporter, dry_run=args.dry_run)

        # If focus specified, modify initial prompt
        if args.focus:
            agent.messages = [
                {"role": "user", "content": f"Begin testing the application, focusing on: {args.focus}. Start by getting the page state."}
            ]

        print("\nStarting QA session...")
        summary = agent.run(max_steps=args.max_steps)

        # Print results
        print("\n" + "=" * 50)
        print("SESSION COMPLETE")
        print("=" * 50)
        print(f"Steps taken: {agent.step_count}")
        print(f"Issues created: {agent.issues_created}")
        print(f"\nSummary:\n{summary}")

    finally:
        browser.stop()
        print("\nBrowser closed.")


if __name__ == "__main__":
    main()
```

**Step 2: Test the full agent (dry run)**

Run:
```bash
python main.py --dry-run --max-steps 10
```

Expected: Agent runs for up to 10 steps, explores the site, prints what issues it would create.

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point with CLI"
```

---

### Task 7: Final Testing and Documentation

**Files:**
- Update: `README.md` (optional, if desired)

**Step 1: Full test run (still dry run)**

Run:
```bash
python main.py --dry-run --max-steps 20
```

Review the output. Verify:
- Agent navigates the site
- Agent finds elements and interacts with them
- Agent identifies potential bugs or features
- No crashes or unhandled exceptions

**Step 2: Live run (creates real issues)**

When satisfied with dry run:
```bash
python main.py --max-steps 30
```

Check the GitHub repo for created issues.

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: complete browsing agent implementation"
```

---

## Summary

After completing all tasks, you'll have:

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point |
| `agent.py` | Claude API agent with tool loop |
| `browser.py` | Playwright browser controller |
| `github_reporter.py` | GitHub issue creation |
| `config.py` | Environment config |
| `requirements.txt` | Dependencies |
| `.env.example` | Credential template |

**Usage:**
```bash
# Dry run (no issues created)
python main.py --dry-run

# Full run
python main.py

# Focus on specific feature
python main.py --focus "add part"

# Headless mode
python main.py --headless
```
