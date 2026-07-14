#request와 response 형식 정의
from typing import Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    cardId: int = Field(..., ge=1, description="카드 ID")
    title: str = Field(..., min_length=1, max_length=100, description="프로젝트 제목")
    content: str = Field(..., min_length=1, max_length=1000, description="프로젝트 설명")


class RepositoryRecommendation(BaseModel):
    repositoryId: int
    name: str
    fullName: str
    url: str
    description: Optional[str] = None
    language: Optional[str] = None
    techStack: list[str] = Field(default_factory=list)
    stars: int
    forks: int
    updatedAt: str
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    cardId: int
    recommendation: Optional[RepositoryRecommendation] = None
    message: str