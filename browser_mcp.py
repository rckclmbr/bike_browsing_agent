#!/usr/bin/env python3
"""MCP server exposing browser and GitHub tools to Claude CLI."""

import asyncio
import os
import atexit
from mcp.server.fastmcp import FastMCP
from browser import BrowserController
from github_reporter import GitHubReporter
from config import config

mcp = FastMCP("crankcase-qa")

# Global state
browser: BrowserController | None = None
reporter: GitHubReporter | None = None
dry_run: bool = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
issues_created: int = 0


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
            pass  # Best effort cleanup
        browser = None


atexit.register(cleanup)


@mcp.tool()
async def start_browser(headless: bool = False) -> str:
    """Start the browser and log in to the application. Call this first before any other browser tools."""
    global browser, reporter

    if browser:
        return "Browser already running"

    browser = BrowserController(headless=headless)
    await browser.start()
    result = await browser.login()
    reporter = GitHubReporter()

    status = result.get("status", "unknown")
    if status == "ok":
        return f"Browser started and logged in as {result.get('user', 'unknown')}. URL: {result.get('url')}"
    else:
        return f"Browser started but login failed: {result.get('message', 'unknown error')}. Continuing anyway."


@mcp.tool()
async def stop_browser() -> str:
    """Close the browser when done testing. Call this when finished."""
    global browser

    if not browser:
        return "Browser not running"

    await browser.stop()
    browser = None
    return "Browser closed"


@mcp.tool()
async def get_page_state() -> dict:
    """Get the current page URL, title, and simplified HTML showing interactive elements."""
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


@mcp.tool()
async def fill(selector: str, text: str) -> dict:
    """Fill a text input field with the given text."""
    if not browser:
        return {"error": "Browser not started. Call start_browser first."}
    return await browser.fill(selector, text)


@mcp.tool()
async def select(selector: str, value: str) -> dict:
    """Select an option from a dropdown by value."""
    if not browser:
        return {"error": "Browser not started. Call start_browser first."}
    return await browser.select(selector, value)


@mcp.tool()
async def screenshot() -> dict:
    """Take a screenshot of the current page. Use sparingly - only when you suspect a visual bug."""
    if not browser:
        return {"error": "Browser not started. Call start_browser first."}

    os.makedirs("screenshots", exist_ok=True)

    # Find next available screenshot number
    existing = [f for f in os.listdir("screenshots") if f.startswith("screenshot_")]
    num = len(existing) + 1
    path = f"screenshots/screenshot_{num}.png"

    result = await browser.screenshot(path)
    result["note"] = "Screenshot saved. Describe what you expected to see vs what appears."
    return result


@mcp.tool()
def report_bug(title: str, description: str, steps_to_reproduce: str) -> dict:
    """Report a bug found during testing. Include specific steps to reproduce."""
    global issues_created

    if not reporter:
        return {"error": "Browser not started. Call start_browser first."}

    if dry_run:
        return {"status": "dry_run", "would_create": "bug", "title": title}

    if issues_created >= config.MAX_ISSUES:
        return {"status": "skipped", "reason": f"Max issues ({config.MAX_ISSUES}) already created"}

    result = reporter.create_bug(title, description, steps_to_reproduce)
    if result.get("status") == "created":
        issues_created += 1
    return result


@mcp.tool()
def report_feature_request(title: str, description: str, rationale: str) -> dict:
    """Suggest a feature or improvement. Explain what it should do and why it would be valuable."""
    global issues_created

    if not reporter:
        return {"error": "Browser not started. Call start_browser first."}

    if dry_run:
        return {"status": "dry_run", "would_create": "feature_request", "title": title}

    if issues_created >= config.MAX_ISSUES:
        return {"status": "skipped", "reason": f"Max issues ({config.MAX_ISSUES}) already created"}

    result = reporter.create_feature_request(title, description, rationale)
    if result.get("status") == "created":
        issues_created += 1
    return result


if __name__ == "__main__":
    mcp.run()
