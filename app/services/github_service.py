import requests
from fastapi import HTTPException

from app.core.config import settings


def _build_headers() -> dict:

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    return headers


def _normalize_repository(repo: dict) -> dict:

    return {
        "repositoryId": repo.get("id") or 0,
        "name": repo.get("name") or "",
        "fullName": repo.get("full_name") or "",
        "url": repo.get("html_url") or "",
        "description": repo.get("description") or "",
        "language": repo.get("language"),
        "topics": repo.get("topics") or [],
        "stars": repo.get("stargazers_count") or 0,
        "forks": repo.get("forks_count") or 0,
        "updatedAt": repo.get("updated_at") or "",
        "archived": repo.get("archived") or False,
        "fork": repo.get("fork") or False,
        "openIssues": repo.get("open_issues_count") or 0,
    }


def search_repositories(query: str, per_page: int = 30) -> list[dict]:

    url = f"{settings.GITHUB_API_URL.rstrip('/')}/search/repositories"

    params = {
        "q": query,
        "per_page": per_page,
    }

    try:
        response = requests.get(
            url,
            headers=_build_headers(),
            params=params,
            timeout=settings.GITHUB_TIMEOUT,
        )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"GitHub API 오류: {response.status_code}, {response.text}",
            )

        data = response.json()
        items = data.get("items", [])

        return [_normalize_repository(repo) for repo in items]

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"GitHub API 처리 중 서버 오류가 발생했습니다: {str(error)}",
        )