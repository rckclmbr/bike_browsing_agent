import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    CRANKCASE_URL: str = os.environ["CRANKCASE_URL"]
    GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
    GITHUB_REPO: str = os.environ["GITHUB_REPO"]

    # JWT session authentication (for sites using Strava OAuth)
    JWT_SECRET: str = os.environ["JWT_SECRET"]
    SESSION_USER_ID: str = os.environ["SESSION_USER_ID"]
    SESSION_USER_NAME: str = os.environ["SESSION_USER_NAME"]

    # Defaults
    MAX_STEPS: int = int(os.environ.get("MAX_STEPS", "100"))
    MAX_ISSUES: int = int(os.environ.get("MAX_ISSUES", "10"))
    ACTION_TIMEOUT: int = int(os.environ.get("ACTION_TIMEOUT", "30000"))  # ms


config = Config()
