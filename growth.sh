#!/bin/bash
set -e

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

PHASE="${1:-research}"
CHANNEL="${2:-}"

case "$PHASE" in
    research)
        echo "=================================="
        echo "Growth Agent - Phase 1: Research"
        echo "=================================="
        echo

        PROMPT="You are a growth marketer for CrankCase, a bike maintenance tracking application.

Background: You ride 200+ miles per week and know the cycling community inside out. You previously grew a cycling newsletter to 50k subscribers through grassroots community building. You know where cyclists hang out online, what content resonates, and how to build authentic community without being spammy.

Your goal in this phase is to:
1. Identify the best channels to acquire cyclists who care about bike maintenance
2. Analyze what competitors/alternatives exist and how they acquire users
3. Propose 3-5 growth channels ranked by potential impact and effort

Research and analyze:
- **Online communities**: Reddit (r/cycling, r/bikewrench, r/velo), cycling forums, Facebook groups, Strava clubs
- **Content platforms**: YouTube bike maintenance channels, cycling podcasts, blogs
- **Competitors**: How do apps like ProBikeGarage, BikeIndex, Strava itself acquire users?
- **Partnerships**: Bike shops, cycling coaches, team managers, bike fitters
- **Influencers**: Cycling YouTubers, Instagram mechanics, pro team mechanics

For each channel, consider:
- Audience size and relevance
- Cost (time/money) to acquire users
- Authenticity fit (will it feel spammy?)
- Viral potential (do users bring other users?)

When done, call save_strategy with filename 'growth-channels' containing:
- Executive summary of growth opportunity
- Ranked list of 3-5 channels with:
  - Channel name and description
  - Why it works for CrankCase
  - Estimated reach and conversion potential
  - Effort level (low/medium/high)
  - Specific tactics to try
- Recommended starting point

Be specific and actionable. Think like a scrappy startup, not a Fortune 500 marketing department."

        claude --print \
               --dangerously-skip-permissions \
               --mcp-config '{"mcpServers":{"growth-agent":{"command":"python","args":["'"$(pwd)/growth_mcp.py"'"]}}}' \
               -p "$PROMPT"

        echo
        echo "=================================="
        echo "Research saved to docs/strategy/growth-channels.md"
        echo "Review it, then run:"
        echo "  ./growth.sh execute \"Channel name\""
        echo "=================================="
        ;;

    execute)
        if [ -z "$CHANNEL" ]; then
            echo "Usage: ./growth.sh execute \"Channel name\""
            echo "Example: ./growth.sh execute \"Reddit Community Building\""
            exit 1
        fi

        echo "=================================="
        echo "Growth Agent - Phase 2: Execute"
        echo "=================================="
        echo "Channel: $CHANNEL"
        echo "=================================="
        echo

        PROMPT="You are a growth marketer executing on this channel: $CHANNEL

Background: You ride 200+ miles per week and know the cycling community inside out. You previously grew a cycling newsletter to 50k subscribers. You know how to build authentic community without being spammy.

Your goal is to:
1. Read the growth research for context
2. Create a detailed campaign plan for this channel
3. Break it down into actionable GitHub issues

Instructions:
1. Call read_file with path 'docs/strategy/growth-channels.md' to get context
2. Call save_strategy with a descriptive filename and detailed campaign plan including:
   - Channel overview and why we're prioritizing it
   - Target audience within this channel
   - Content/messaging strategy
   - Week-by-week rollout plan (4 weeks)
   - Success metrics and how to measure them
   - Risks and how to avoid looking spammy

3. Create 5-10 GitHub issues that execute this campaign:
   - Each issue should be a specific, completable task
   - Use clear titles: 'Write intro post for r/bikewrench' or 'Create YouTube shorts content plan'
   - Include in the body:
     - '## Context' section linking to the campaign doc
     - '## Task' section with clear deliverable
     - '## Guidelines' with tone, length, dos/don'ts
   - Label issues with 'marketing' and 'growth'

4. Summarize what you created

Make issues specific enough that someone unfamiliar with the strategy could execute them. Include example copy/talking points where helpful."

        claude --print \
               --dangerously-skip-permissions \
               --mcp-config '{"mcpServers":{"growth-agent":{"command":"python","args":["'"$(pwd)/growth_mcp.py"'"]}}}' \
               -p "$PROMPT"

        echo
        echo "=================================="
        echo "Campaign plan and issues created!"
        echo "=================================="
        ;;

    *)
        echo "Usage: ./growth.sh [research|execute] [channel]"
        echo
        echo "Phases:"
        echo "  research            - Research growth channels and opportunities"
        echo "  execute \"channel\"  - Create campaign plan and issues for a channel"
        echo
        echo "Examples:"
        echo "  ./growth.sh research"
        echo "  ./growth.sh execute \"Reddit Community Building\""
        exit 1
        ;;
esac
