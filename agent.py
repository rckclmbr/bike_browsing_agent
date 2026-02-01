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
