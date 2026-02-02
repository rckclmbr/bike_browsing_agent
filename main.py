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
        login_result = browser.login()
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
