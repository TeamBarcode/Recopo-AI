import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings
from app.services.filtering_service import deduplicate_repositories, filter_repositories
from app.services.github_service import get_repository_readme, search_repositories


SEED_QUERIES = [
    "pose estimation webcam",
    "fitness posture correction",
    "workout posture correction",
    "opencv mediapipe fitness",
    "human pose estimation app",
    "computer vision exercise app",

    "recommendation system web app",
    "movie recommendation system",
    "music recommendation system",
    "restaurant recommendation app",
    "content based recommender",
    "collaborative filtering recommender",

    "chatbot web app",
    "ai chatbot fastapi",
    "llm chatbot react",
    "customer service chatbot",

    "todo task management web app",
    "calendar schedule app",
    "kanban task management",

    "fastapi react project",
    "django react project",
    "flask react app",
    "nextjs fastapi app",

    "computer vision web app",
    "image classification web app",
    "object detection web app",
    "opencv web application",
]


def collect_repositories() -> list[dict]:

    repositories = []

    for query in SEED_QUERIES:
        print(f"[검색] {query}")

        try:
            search_result = search_repositories(query=query, per_page=30)
            repositories.extend(search_result)
        except Exception as error:
            print(f"[검색 실패] {query}: {error}")

    repositories = deduplicate_repositories(repositories)
    repositories = filter_repositories(repositories, min_stars=1)

    collected = []

    for index, repo in enumerate(repositories, start=1):
        full_name = repo.get("fullName") or ""

        print(f"[README 수집] {index}/{len(repositories)} {full_name}")

        readme = get_repository_readme(full_name)

        if not readme:
            continue

        repo_with_readme = repo.copy()
        repo_with_readme["readme"] = readme

        collected.append(repo_with_readme)

    return collected


def save_repositories(repositories: list[dict]) -> None:

    output_path = Path(settings.REPOSITORY_DATA_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(repositories, file, ensure_ascii=False, indent=2)

    print(f"[저장 완료] {output_path}")
    print(f"[수집 개수] {len(repositories)}")


if __name__ == "__main__":
    result = collect_repositories()
    save_repositories(result)
