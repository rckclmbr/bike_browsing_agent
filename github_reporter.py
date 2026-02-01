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
