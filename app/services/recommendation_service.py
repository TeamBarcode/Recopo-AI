import re

from app.core.config import settings
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RepositoryRecommendation,
)
from app.services.filtering_service import (
    deduplicate_repositories,
    filter_repositories,
)
from app.services.github_service import (
    get_repository_readme,
    search_repositories,
)
from app.services.query_service import query_service
from app.services.rag_service import recommend_repositories_with_rag
from app.services.ranking_service import rank_repositories
from app.services.reason_service import generate_recommendation_reason


TECH_NAME_MAP = {
    "opencv": "OpenCV",
    "mediapipe": "MediaPipe",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "react": "React",
    "nextjs": "Next.js",
    "vue": "Vue",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "machine-learning": "Machine Learning",
    "deep-learning": "Deep Learning",
    "computer-vision": "Computer Vision",
    "pose-estimation": "Pose Estimation",
    "human-pose-estimation": "Human Pose Estimation",
    "posture-correction": "Posture Correction",
    "real-time": "Real Time",
    "webcam": "Webcam",
}


def _format_topic(topic: str) -> str:
    topic_lower = topic.lower()

    if topic_lower in TECH_NAME_MAP:
        return TECH_NAME_MAP[topic_lower]

    return topic.replace("-", " ").title()


def _build_tech_stack(repo: dict) -> list[str]:
    tech_stack = []
    language = repo.get("language")

    if language:
        tech_stack.append(language)

    for topic in repo.get("topics") or []:
        formatted_topic = _format_topic(topic)

        if formatted_topic not in tech_stack:
            tech_stack.append(formatted_topic)

        if len(tech_stack) >= 5:
            break

    return tech_stack


def _extract_search_terms(search_query: str) -> list[str]:
    terms = re.findall(
        r"[A-Za-z0-9가-힣][A-Za-z0-9가-힣.+#-]*",
        search_query.lower(),
    )

    return list(dict.fromkeys(terms))[:20]


def _build_github_query(search_query: str) -> str:
    return " ".join(search_query.split())[:256]


def _collect_repositories(search_query: str) -> list[dict]:
    github_query = _build_github_query(search_query)

    repositories = search_repositories(
        query=github_query,
        per_page=settings.GITHUB_SEARCH_PER_PAGE,
    )

    return deduplicate_repositories(repositories)


def _attach_readme_to_repositories(
    repositories: list[dict],
) -> list[dict]:
    enriched_repositories = []

    for repo in repositories:
        repo_with_readme = repo.copy()
        full_name = repo_with_readme.get("fullName") or ""

        repo_with_readme["readme"] = get_repository_readme(
            full_name
        )

        enriched_repositories.append(repo_with_readme)

    return enriched_repositories


def _to_repository_recommendation(
    repo: dict,
) -> RepositoryRecommendation:
    return RepositoryRecommendation(
        repositoryId=repo.get("repositoryId", 0),
        name=repo.get("name", ""),
        fullName=repo.get("fullName", ""),
        url=repo.get("url", ""),
        description=repo.get("description", ""),
        language=repo.get("language"),
        techStack=_build_tech_stack(repo),
        stars=repo.get("stars", 0),
        forks=repo.get("forks", 0),
        updatedAt=repo.get("updatedAt", ""),
        reason=repo.get(
            "reason",
            "입력된 아이디어와 유사한 레포지토리입니다.",
        ),
    )


def _exclude_repositories(
    repositories: list[dict],
    excluded_repository_ids: list[int],
) -> list[dict]:
    if not excluded_repository_ids:
        return repositories

    excluded_ids = set(excluded_repository_ids)

    return [
        repo
        for repo in repositories
        if repo.get("repositoryId") not in excluded_ids
    ]


def _get_fallback_recommendations(
    search_query: str,
    search_terms: list[str],
) -> list[dict]:
    repositories = _collect_repositories(search_query)

    if not repositories:
        return []

    filtered_repositories = filter_repositories(
        repositories
    )

    if not filtered_repositories:
        return []

    metadata_ranked_repositories = rank_repositories(
        repositories=filtered_repositories,
        keywords=search_terms,
        use_readme=False,
    )

    readme_target_repositories = metadata_ranked_repositories[
        : settings.GITHUB_README_CANDIDATE_LIMIT
    ]

    enriched_repositories = _attach_readme_to_repositories(
        readme_target_repositories
    )

    return rank_repositories(
        repositories=enriched_repositories,
        keywords=search_terms,
        use_readme=True,
    )


def get_repository_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:
    query_result = query_service.build_search_query(
        title=request.title,
        content=request.content,
    )


    search_query = query_result.search_query
    search_terms = _extract_search_terms(search_query)

    rag_ranked_repositories = recommend_repositories_with_rag(
        search_query=search_query,
    )

    rag_ranked_repositories = _exclude_repositories(
        repositories=rag_ranked_repositories,
        excluded_repository_ids=request.excludedRepositoryIds,
    )

    if rag_ranked_repositories:
        best_repository = rag_ranked_repositories[0]

    else:
        fallback_repositories = _get_fallback_recommendations(
            search_query=search_query,
            search_terms=search_terms,
        )

        fallback_repositories = _exclude_repositories(
            repositories=fallback_repositories,
            excluded_repository_ids=request.excludedRepositoryIds,
        )

        if not fallback_repositories:
            return RecommendationResponse(
                cardId=request.cardId,
                recommendation=None,
            )

        best_repository = fallback_repositories[0]

    best_repository["reason"] = generate_recommendation_reason(
        repo=best_repository,
        keywords=search_terms,
        title=request.title,
        content=request.content,
    )

    recommendation = _to_repository_recommendation(
        best_repository
    )

    return RecommendationResponse(
        cardId=request.cardId,
        recommendation=recommendation,
    )