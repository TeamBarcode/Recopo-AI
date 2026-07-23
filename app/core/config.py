import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_API_URL: str = os.getenv("GITHUB_API_URL", "https://api.github.com")
    GITHUB_TIMEOUT: int = int(os.getenv("GITHUB_TIMEOUT", "10"))

    GITHUB_SEARCH_PER_PAGE: int = int(os.getenv("GITHUB_SEARCH_PER_PAGE", "30"))
    GITHUB_README_CANDIDATE_LIMIT: int = int(
        os.getenv("GITHUB_README_CANDIDATE_LIMIT", "10")
    )
    GITHUB_README_MAX_CHARS: int = int(
        os.getenv("GITHUB_README_MAX_CHARS", "4000")
    )

    MIN_REPOSITORY_STARS: int = int(os.getenv("MIN_REPOSITORY_STARS", "5"))


settings = Settings()