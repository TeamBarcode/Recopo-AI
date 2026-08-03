from fastapi import APIRouter

from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.rag_service import recommend_repositories_with_rag
from app.services.recommendation_service import get_repository_recommendation

router = APIRouter()


@router.post("", response_model=RecommendationResponse)
def recommend_repository(request: RecommendationRequest) -> RecommendationResponse:
    return get_repository_recommendation(request)


@router.post("/debug/top5")
def debug_recommend_repositories_top5(request: RecommendationRequest) -> dict:
    repositories = recommend_repositories_with_rag(
        title=request.title,
        content=request.content,
        top_k=30,
    )

    excluded_ids = set(request.excludedRepositoryIds or [])

    filtered_repositories = [
        repo
        for repo in repositories
        if repo.get("repositoryId") not in excluded_ids
    ]

    return {
        "cardId": request.cardId,
        "count": len(filtered_repositories[:5]),
        "recommendations": filtered_repositories[:5],
    }