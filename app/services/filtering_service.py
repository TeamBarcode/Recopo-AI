# 추천하기 애매한 레포 제거.
def filter_repositories(repositories: list[dict], min_stars: int = 5) -> list[dict]:
 
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

    # 조건이 너무 엄격해서 결과가 없으면 stars 조건만 완화한다.
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