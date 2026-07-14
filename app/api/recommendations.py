# 실제 API 주소 만들기.
from fastapi import APIRouter

from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import get_repository_recommendation


router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
def recommend_repository(request: RecommendationRequest) -> RecommendationResponse:

    return get_repository_recommendation(request)