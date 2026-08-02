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
from app.services.query_service import create_search_queries, extract_keywords
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
    """
    language + topics를 기반으로 techStack을 만든다.
    """
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


def _collect_repositories(search_queries: list[str]) -> list[dict]:
    """
    여러 검색 query로 GitHub API를 호출하고 후보 레포를 수집한다.
    기존 final-pipeline fallback에서 사용한다.
    """
    repositories = []

    for query in search_queries:
        search_result = search_repositories(
            query=query,
            per_page=settings.GITHUB_SEARCH_PER_PAGE,
        )
        repositories.extend(search_result)

    return deduplicate_repositories(repositories)


def _attach_readme_to_repositories(repositories: list[dict]) -> list[dict]:
    """
    상위 후보 레포에 README 내용을 추가한다.
    기존 final-pipeline fallback에서 사용한다.
    """
    enriched_repositories = []

    for repo in repositories:
        repo_with_readme = repo.copy()
        full_name = repo_with_readme.get("fullName") or ""

        repo_with_readme["readme"] = get_repository_readme(full_name)

        enriched_repositories.append(repo_with_readme)

    return enriched_repositories


def _to_repository_recommendation(repo: dict) -> RepositoryRecommendation:
    """
    내부 dict 형태의 repo를 API response schema로 변환한다.
    BE에 보내는 형식은 기존과 동일하게 유지한다.
    """
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
        score=repo.get("score", 0.0),
        reason=repo.get("reason", "입력된 아이디어와 유사한 레포지토리입니다."),
    )


def _get_fallback_recommendations(
    request: RecommendationRequest,
    keywords: list[str],
) -> list[dict]:
    """
    Vector DB가 비어 있거나 RAG 검색 결과가 없을 때
    기존 final-pipeline 방식으로 추천을 수행한다.

    기존 흐름:
    GitHub API 검색
    → 후보 수집
    → 필터링
    → metadata 기반 1차 랭킹
    → README 조회
    → README 포함 최종 랭킹
    """
    search_queries = create_search_queries(request.title, request.content)

    repositories = _collect_repositories(search_queries)

    if not repositories:
        return []

    filtered_repositories = filter_repositories(repositories)

    if not filtered_repositories:
        return []

    metadata_ranked_repositories = rank_repositories(
        repositories=filtered_repositories,
        keywords=keywords,
        use_readme=False,
    )

    readme_target_repositories = metadata_ranked_repositories[
        : settings.GITHUB_README_CANDIDATE_LIMIT
    ]

    enriched_repositories = _attach_readme_to_repositories(readme_target_repositories)

    return rank_repositories(
        repositories=enriched_repositories,
        keywords=keywords,
        use_readme=True,
    )


def get_repository_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    사용자 입력을 받아 GitHub 레포지토리 1개를 추천한다.

    우선순위:
    1. Vector DB 기반 RAG 추천
    2. RAG 결과가 없으면 기존 final-pipeline 방식 fallback
    """
    keywords = extract_keywords(request.title, request.content)

    rag_ranked_repositories = recommend_repositories_with_rag(
    title=request.title,
    content=request.content,
    )

    rag_ranked_repositories = _exclude_repositories(
        repositories=rag_ranked_repositories,
        excluded_repository_ids=request.excludedRepositoryIds,
    )

    if rag_ranked_repositories:
        best_repository = rag_ranked_repositories[0]
    else:
        fallback_repositories = _get_fallback_recommendations(
            request=request,
            keywords=keywords,
        )

        fallback_repositories = _exclude_repositories(
            repositories=fallback_repositories,
            excluded_repository_ids=request.excludedRepositoryIds,
        )

        if not fallback_repositories:
            return RecommendationResponse(
                cardId=request.cardId,
                recommendation=None,
                message="조건에 맞는 추천 레포지토리를 찾지 못했습니다.",
            )

        best_repository = fallback_repositories[0]

    best_repository["reason"] = generate_recommendation_reason(
        repo=best_repository,
        keywords=keywords,
    )

    recommendation = _to_repository_recommendation(best_repository)

    return RecommendationResponse(
        cardId=request.cardId,
        recommendation=recommendation,
        message="추천 레포지토리를 찾았습니다.",
    )

def _exclude_repositories(
    repositories: list[dict],
    excluded_repository_ids: list[int],
) -> list[dict]:
    """
    이미 추천된 repositoryId를 추천 후보에서 제외한다.
    """
    if not excluded_repository_ids:
        return repositories

    excluded_ids = set(excluded_repository_ids)

    return [
        repo
        for repo in repositories
        if repo.get("repositoryId") not in excluded_ids
    ]