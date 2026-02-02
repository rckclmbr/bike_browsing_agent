#!/usr/bin/env python3
"""Growth Agent - MCP server for marketing research and campaign planning."""

import json
import os
import subprocess
from datetime import date
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("growth-agent")


# =============================================================================
# GitHub Tools (via gh CLI)
# =============================================================================

def _run_gh(args: list[str]) -> dict:
    """Run a gh CLI command and return parsed JSON."""
    try:
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
def create_issue(title: str, body: str, labels: str = "") -> dict:
    """Create a GitHub issue. Labels: comma-separated (e.g., 'marketing,growth')."""
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

    url = result.stdout.strip()
    return {"status": "created", "url": url}


# =============================================================================
# Strategy Tools
# =============================================================================

@mcp.tool()
def save_strategy(filename: str, content: str) -> dict:
    """Save a strategy/research document to docs/strategy/. Returns the file path."""
    os.makedirs("docs/strategy", exist_ok=True)

    clean_name = filename.lower().replace(" ", "-").replace("_", "-")
    if not clean_name.endswith(".md"):
        clean_name += ".md"

    today = date.today().isoformat()
    if not clean_name.startswith("20"):
        clean_name = f"{today}-{clean_name}"

    path = f"docs/strategy/{clean_name}"

    with open(path, "w") as f:
        f.write(content)

    return {"status": "ok", "path": path}


@mcp.tool()
def read_file(path: str) -> dict:
    """Read a file's contents. Use for reading strategy docs or previous research."""
    try:
        with open(path, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
