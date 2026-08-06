# 추천하기 애매한 레포 제거
from app.core.config import settings


def deduplicate_repositories(repositories: list[dict]) -> list[dict]:

    seen_repository_ids = set()
    unique_repositories = []

    for repo in repositories:
        repository_id = repo.get("repositoryId")

        if not repository_id:
            continue

        if repository_id in seen_repository_ids:
            continue

        seen_repository_ids.add(repository_id)
        unique_repositories.append(repo)

    return unique_repositories


def filter_repositories(
    repositories: list[dict],
    min_stars: int | None = None,
) -> list[dict]:

    min_stars = settings.MIN_REPOSITORY_STARS if min_stars is None else min_stars

    filtered = []

    for repo in repositories:
        if repo.get("archived"):
            continue

        if repo.get("fork"):
            continue

        if not repo.get("description"):
            continue

        if repo.get("stars", 0) < min_stars:
            continue

        filtered.append(repo)

    if filtered:
        return filtered

    relaxed = []

    for repo in repositories:
        if repo.get("archived"):
            continue

        if repo.get("fork"):
            continue

        if not repo.get("description"):
            continue

        relaxed.append(repo)

    return relaxed