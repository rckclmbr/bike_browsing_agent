#!/bin/bash
set -e

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Defaults
MAX_TURNS="${1:-20}"
FOCUS="${2:-}"
HEADLESS="${HEADLESS:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Build prompt
PROMPT="You are a thorough QA tester for CrankCase, a bike maintenance tracking application.

Your job is to:
1. Explore the application like a real user would
2. Test the main features and workflows
3. Look for bugs, errors, and UX issues
4. Suggest improvements and missing features

Instructions:
1. First call start_browser to launch the browser and log in
2. Use get_page_state to see what's on the current page
3. Explore navigation and features systematically
4. Test happy paths first, then edge cases
5. Report bugs with report_bug (include exact steps to reproduce)
6. Suggest improvements with report_feature_request
7. When done, call stop_browser and summarize findings

What qualifies as a bug:
- Errors, crashes, or unexpected behavior
- Data not saved or displayed correctly
- Broken links or missing pages

What qualifies as a feature request:
- Missing functionality users would expect
- UX improvements (better labels, confirmations, feedback)
${FOCUS:+
Focus your testing on: $FOCUS}"

# Export for MCP server
export DRY_RUN

echo "=================================="
echo "CrankCase QA Agent"
echo "=================================="
echo "Max turns: $MAX_TURNS"
echo "Headless: $HEADLESS"
echo "Dry run: $DRY_RUN"
[ -n "$FOCUS" ] && echo "Focus: $FOCUS"
echo "=================================="
echo

claude --mcp ./browser_mcp.py \
       --max-turns "$MAX_TURNS" \
       --print \
       -p "$PROMPT"
