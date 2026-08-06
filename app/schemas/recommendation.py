from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    cardId: int
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    excludedRepositoryIds: list[int] = Field(default_factory=list)


class RepositoryRecommendation(BaseModel):
    repositoryId: int
    name: str
    fullName: str
    url: str
    description: str | None = None
    language: str | None = None
    techStack: list[str] = Field(default_factory=list)
    stars: int
    forks: int
    updatedAt: str
    reason: str


class RecommendationResponse(BaseModel):
    cardId: int
    recommendation: RepositoryRecommendation | None