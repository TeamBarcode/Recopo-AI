import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.services.rag_service import recommend_repositories_with_rag


CASES_PATH = ROOT_DIR / "tests" / "manual_recommendation_cases.json"


def main() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    for case in cases:
        title = case["title"]
        content = case["content"]
        excluded_ids = set(case.get("excludedRepositoryIds", []))

        print(f"\n=== {case['cardId']} | {title} ===")

        repositories = recommend_repositories_with_rag(
            title=title,
            content=content,
            top_k=30,
        )

        repositories = [
            repo
            for repo in repositories
            if repo.get("repositoryId") not in excluded_ids
        ][:5]

        if not repositories:
            print("RAG 결과 없음")
            continue

        for index, repo in enumerate(repositories, start=1):
            print(
                f"{index}. {repo.get('fullName')} | "
                f"score={repo.get('score')} | "
                f"ragScore={repo.get('ragScore')} | "
                f"similarity={repo.get('bestSimilarity')}"
            )
            print(f"   repositoryId={repo.get('repositoryId')}")
            print(f"   desc={repo.get('description')}")


if __name__ == "__main__":
    main()