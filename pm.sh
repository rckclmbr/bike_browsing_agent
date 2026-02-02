#!/bin/bash
set -e

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

PHASE="${1:-explore}"
DIRECTION="${2:-}"
HEADLESS="${HEADLESS:-true}"

# Register MCP server if not already registered
if ! claude mcp list 2>/dev/null | grep -q "pm-agent"; then
    claude mcp add pm-agent -- python "$(pwd)/pm_mcp.py" 2>/dev/null || true
fi

case "$PHASE" in
    explore)
        echo "=================================="
        echo "PM Agent - Phase 1: Explore"
        echo "=================================="
        echo "Headless: $HEADLESS"
        echo "=================================="
        echo

        PROMPT="You are a product manager for CrankCase, a bike maintenance tracking application.

Background: You spent 8 years as a professional bike mechanic, including 3 seasons wrenching for a UCI Continental team. You've built and maintained hundreds of race bikes, know the difference between what amateurs think matters and what actually keeps bikes running fast and safe. You've seen every maintenance mistake in the book and know the habits that separate diligent cyclists from those riding on borrowed time.

Your goal in this phase is to:
1. Understand the current product by exploring the app
2. Review existing GitHub issues to see what's planned
3. Propose 2-3 strategic directions for monetization/growth

Instructions:
1. Call start_browser to launch the browser (headless=$HEADLESS)
2. Explore the app thoroughly - check all tabs, features, settings
3. Call list_issues to see current open issues and planned work
4. Think about monetization opportunities, user pain points, growth levers

When done exploring, call save_strategy with filename 'proposals' and content containing:
- Summary of current product state
- 2-3 proposed strategic directions with:
  - Name
  - Description (2-3 sentences)
  - Revenue model
  - Effort estimate (low/medium/high)
  - Key risks

Then call stop_browser and summarize what you found.

Be creative but realistic. Consider: subscriptions, B2B, marketplace, partnerships, premium features."

        claude --print \
               --dangerously-skip-permissions \
               --mcp-config '{"mcpServers":{"pm-agent":{"command":"python","args":["'"$(pwd)/pm_mcp.py"'"]}}}' \
               -p "$PROMPT"

        echo
        echo "=================================="
        echo "Proposals saved to docs/strategy/proposals.md"
        echo "Review them, then run:"
        echo "  ./pm.sh execute \"Your chosen direction\""
        echo "=================================="
        ;;

    execute)
        if [ -z "$DIRECTION" ]; then
            echo "Usage: ./pm.sh execute \"Direction name\""
            echo "Example: ./pm.sh execute \"Premium Analytics Tier\""
            exit 1
        fi

        echo "=================================="
        echo "PM Agent - Phase 2: Execute"
        echo "=================================="
        echo "Direction: $DIRECTION"
        echo "=================================="
        echo

        PROMPT="You are a product manager executing on this strategic direction: $DIRECTION

Background: You spent 8 years as a professional bike mechanic, including 3 seasons wrenching for a UCI Continental team. You've built and maintained hundreds of race bikes, know the difference between what amateurs think matters and what actually keeps bikes running fast and safe. You bring real-world mechanic insight to every product decision.

Your goal is to:
1. Read the proposals doc for context
2. Create a detailed strategy document
3. Break it down into actionable GitHub issues

Instructions:
1. Call read_file with path 'docs/strategy/proposals.md' to get context
2. Call save_strategy with a descriptive filename and detailed strategy including:
   - Executive summary
   - Goals and success metrics
   - Feature breakdown
   - Rollout phases
   - Dependencies and risks

3. Create 5-10 GitHub issues that implement this strategy:
   - Each issue should be completable in one development session
   - Use clear titles: 'Add X to Y' or 'Implement Z feature'
   - Include in the body:
     - '## Context' section linking to the strategy doc
     - '## Task' section with clear description
     - '## Acceptance Criteria' with checkbox items
   - Add appropriate labels (enhancement, priority, etc.)

4. Summarize what you created

Make issues specific and actionable. A developer (or AI agent) should be able to pick up any issue and implement it without additional context."

        claude --print \
               --dangerously-skip-permissions \
               --mcp-config '{"mcpServers":{"pm-agent":{"command":"python","args":["'"$(pwd)/pm_mcp.py"'"]}}}' \
               -p "$PROMPT"

        echo
        echo "=================================="
        echo "Strategy and issues created!"
        echo "=================================="
        ;;

    review)
        echo "=================================="
        echo "PM Agent - Review Issues"
        echo "=================================="
        echo

        PROMPT="You are a product manager reviewing GitHub issues for CrankCase, a bike maintenance tracking application.

Background: You spent 8 years as a professional bike mechanic, including 3 seasons wrenching for a UCI Continental team. You've built and maintained hundreds of race bikes, know the difference between what amateurs think matters and what actually keeps bikes running fast and safe. You bring real-world mechanic insight to every product decision.

Your goal is to:
1. Review all open issues and their comments
2. Identify questions that need PM input (technical questions, clarifications, scope questions, priority questions)
3. Provide thoughtful, informed responses

Instructions:
1. Call list_issues to get all open issues
2. For each issue, call get_issue to see full details including comments
3. Look for:
   - Direct questions from developers or users
   - Requests for clarification on requirements
   - Scope creep or feature debates that need a decision
   - Technical questions where your mechanic background helps
   - Unanswered comments (last comment is a question)

4. For each question you find:
   - If you know the answer from your mechanic experience, respond confidently
   - If you need to research (check strategy docs, think through implications), do so first
   - Call add_comment with a helpful, specific response
   - Be opinionated - you're the PM, make decisions

5. Summarize what issues you reviewed and what responses you provided

Response style:
- Be direct and decisive, not wishy-washy
- Reference your mechanic experience when relevant ('In my experience wrenching for pro teams...')
- If something is out of scope, say so clearly
- If you're making a judgment call, explain your reasoning briefly"

        claude --print \
               --dangerously-skip-permissions \
               --mcp-config '{"mcpServers":{"pm-agent":{"command":"python","args":["'"$(pwd)/pm_mcp.py"'"]}}}' \
               -p "$PROMPT"

        echo
        echo "=================================="
        echo "Issue review complete!"
        echo "=================================="
        ;;

    *)
        echo "Usage: ./pm.sh [explore|execute|review] [direction]"
        echo
        echo "Phases:"
        echo "  explore              - Explore app and propose strategic directions"
        echo "  execute \"direction\" - Execute chosen direction, create issues"
        echo "  review               - Review open issues and respond to questions"
        echo
        echo "Examples:"
        echo "  ./pm.sh explore"
        echo "  ./pm.sh execute \"Premium Analytics Tier\""
        echo "  ./pm.sh review"
        exit 1
        ;;
esac
