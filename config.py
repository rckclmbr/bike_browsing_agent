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
