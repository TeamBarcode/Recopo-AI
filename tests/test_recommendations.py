from fastapi.testclient import TestClient

import app.api.recommendations as recommendations_api
from app.main import app
from app.schemas.recommendation import (
    RecommendationResponse,
    RepositoryRecommendation,
)


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommendation_api_success(monkeypatch):
    def fake_get_repository_recommendation(request):
        return RecommendationResponse(
            cardId=request.cardId,
            recommendation=RepositoryRecommendation(
                repositoryId=123456,
                name="pose-estimation-web",
                fullName="owner/pose-estimation-web",
                url="https://github.com/owner/pose-estimation-web",
                description="Real-time pose estimation web application",
                language="Python",
                techStack=["Python", "OpenCV", "MediaPipe"],
                stars=850,
                forks=120,
                updatedAt="2026-06-20T12:30:00Z",
                reason="입력된 아이디어와 유사한 레포지토리입니다.",
            )
        )

    monkeypatch.setattr(
        recommendations_api,
        "get_repository_recommendation",
        fake_get_repository_recommendation,
    )

    response = client.post(
        "/api/recommendations",
        json={
            "cardId": 15,
            "title": "AI 운동 자세 교정 서비스",
            "content": "웹캠으로 사용자의 운동 자세를 분석하고 잘못된 자세를 실시간으로 알려주는 웹서비스",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["cardId"] == 15
    assert data["recommendation"] is not None
    assert data["recommendation"]["repositoryId"] == 123456
    assert data["recommendation"]["name"] == "pose-estimation-web"
    assert data["recommendation"]["url"] == "https://github.com/owner/pose-estimation-web"



def test_recommendation_api_empty_result(monkeypatch):
    def fake_get_repository_recommendation(request):
        return RecommendationResponse(
            cardId=request.cardId,
            recommendation=None,
        )

    monkeypatch.setattr(
        recommendations_api,
        "get_repository_recommendation",
        fake_get_repository_recommendation,
    )

    response = client.post(
        "/api/recommendations",
        json={
            "cardId": 15,
            "title": "희귀한 프로젝트",
            "content": "검색 결과가 없다고 가정하는 테스트입니다.",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["cardId"] == 15
    assert data["recommendation"] is None
    

def test_recommendation_api_validation_error():
    response = client.post(
        "/api/recommendations",
        json={
            "cardId": 15,
            "title": "",
            "content": "내용은 있지만 title이 비어 있는 잘못된 요청",
        },
    )

    assert response.status_code == 422