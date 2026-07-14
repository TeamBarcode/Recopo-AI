#하나의 추천 흐름으로 연결.
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RepositoryRecommendation,
)
from app.services.filtering_service import filter_repositories
from app.services.github_service import search_repositories
from app.services.query_service import create_search_query, extract_keywords
from app.services.ranking_service import rank_repositories


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
    "computer-vision": "Computer Vision",
    "pose-estimation": "Pose Estimation",
    "human-pose-estimation": "Human Pose Estimation",
    "posture-correction": "Posture Correction",
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


def _to_repository_recommendation(repo: dict) -> RepositoryRecommendation:

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


def get_repository_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:

    keywords = extract_keywords(request.title, request.content)
    search_query = create_search_query(request.title, request.content)

    repositories = search_repositories(search_query, per_page=30)

    if not repositories:
        return RecommendationResponse(
            cardId=request.cardId,
            recommendation=None,
            message="GitHub에서 검색 결과를 찾지 못했습니다.",
        )

    filtered_repositories = filter_repositories(repositories)

    if not filtered_repositories:
        return RecommendationResponse(
            cardId=request.cardId,
            recommendation=None,
            message="조건에 맞는 추천 레포지토리를 찾지 못했습니다.",
        )

    ranked_repositories = rank_repositories(filtered_repositories, keywords)

    if not ranked_repositories:
        return RecommendationResponse(
            cardId=request.cardId,
            recommendation=None,
            message="추천 가능한 레포지토리를 찾지 못했습니다.",
        )

    best_repository = ranked_repositories[0]
    recommendation = _to_repository_recommendation(best_repository)

    return RecommendationResponse(
        cardId=request.cardId,
        recommendation=recommendation,
        message="추천 레포지토리를 찾았습니다.",
    )