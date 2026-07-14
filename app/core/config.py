#.env 값을 코드에서 쓸 수 있게 불러오는 파일
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_API_URL: str = os.getenv("GITHUB_API_URL", "https://api.github.com")
    GITHUB_TIMEOUT: int = 10


settings = Settings()