#!/usr/bin/env python3
"""PM Agent - MCP server for product strategy and issue creation."""

import asyncio
import json
import os
import subprocess
import atexit
from datetime import date
from mcp.server.fastmcp import FastMCP
from browser import BrowserController
from config import config

mcp = FastMCP("pm-agent")

# Global state
browser: BrowserController | None = None


def cleanup():
    """Ensure browser is closed on exit."""
    global browser
    if browser:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(browser.stop())
            else:
                loop.run_until_complete(browser.stop())
        except Exception:
            pass
        browser = None


atexit.register(cleanup)


# =============================================================================
# Browser Tools (reused from QA agent)
# =============================================================================

@mcp.tool()
async def start_browser(headless: bool = True) -> str:
    """Start the browser and log in to the application. Call this first."""
    global browser

    if browser:
        return "Browser already running"

    browser = BrowserController(headless=headless)
    await browser.start()
    result = await browser.login()

    status = result.get("status", "unknown")
    if status == "ok":
        return f"Browser started and logged in as {result.get('user', 'unknown')}. URL: {result.get('url')}"
    else:
        return f"Browser started but login failed: {result.get('message', 'unknown error')}. Continuing anyway."


@mcp.tool()
async def stop_browser() -> str:
    """Close the browser when done."""
    global browser

    if not browser:
        return "Browser not running"

    await browser.stop()
    browser = None
    return "Browser closed"


@mcp.tool()
async def get_page_state() -> dict:
    """Get the current page URL, title, and interactive elements."""
    if not browser:
        return {"error": "Browser not started. Call start_browser first."}
    return await browser.get_page_state()


@mcp.tool()
async def navigate(url: str) -> dict:
    """Navigate to a URL."""
    if not browser:
        return {"error": "Browser not started. Call start_browser first."}
    return await browser.navigate(url)


@mcp.tool()
async def click(selector: str) -> dict:
    """Click on an element using a CSS selector."""
    if not browser:
        return {"error": "Browser not started. Call start_browser first."}
    return await browser.click(selector)


# =============================================================================
# GitHub Tools (via gh CLI)
# =============================================================================

def _run_gh(args: list[str]) -> dict:
    """Run a gh CLI command and return parsed JSON."""
    try:
        # Use GITHUB_REPO from env if set
        repo = os.environ.get("GITHUB_REPO", "")
        if repo and "--repo" not in args:
            args = ["--repo", repo] + args

        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        if result.stdout.strip():
            return json.loads(result.stdout)
        return {"status": "ok"}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out"}
    except json.JSONDecodeError:
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_issues(state: str = "open", labels: str = "") -> dict:
    """List GitHub issues. State: open, closed, or all. Labels: comma-separated."""
    args = ["issue", "list", "--json", "number,title,labels,state,body", "--limit", "50", "--state", state]
    if labels:
        args.extend(["--label", labels])
    return _run_gh(args)


@mcp.tool()
def list_prs(state: str = "open") -> dict:
    """List pull requests. State: open, closed, merged, or all."""
    args = ["pr", "list", "--json", "number,title,state,headRefName", "--limit", "20", "--state", state]
    return _run_gh(args)


@mcp.tool()
def get_issue(number: int) -> dict:
    """Get full details of a specific issue including comments."""
    args = ["issue", "view", str(number), "--json", "number,title,body,labels,comments,state"]
    return _run_gh(args)


@mcp.tool()
def create_issue(title: str, body: str, labels: str = "") -> dict:
    """Create a GitHub issue. Labels: comma-separated (e.g., 'enhancement,priority')."""
    repo = os.environ.get("GITHUB_REPO", "")
    args = ["gh", "issue", "create", "--title", title, "--body", body]
    if repo:
        args.extend(["--repo", repo])
    if labels:
        for label in labels.split(","):
            args.extend(["--label", label.strip()])

    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    # gh issue create outputs the URL
    url = result.stdout.strip()
    return {"status": "created", "url": url}


# =============================================================================
# Strategy Tools
# =============================================================================

@mcp.tool()
def save_strategy(filename: str, content: str) -> dict:
    """Save a strategy document to docs/strategy/. Returns the file path."""
    os.makedirs("docs/strategy", exist_ok=True)

    # Clean filename
    clean_name = filename.lower().replace(" ", "-").replace("_", "-")
    if not clean_name.endswith(".md"):
        clean_name += ".md"

    # Add date prefix if not present
    today = date.today().isoformat()
    if not clean_name.startswith("20"):
        clean_name = f"{today}-{clean_name}"

    path = f"docs/strategy/{clean_name}"

    with open(path, "w") as f:
        f.write(content)

    return {"status": "ok", "path": path}


@mcp.tool()
def read_file(path: str) -> dict:
    """Read a file's contents. Use for reading strategy docs or proposals."""
    try:
        with open(path, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
