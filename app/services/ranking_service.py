# 후보 레포마다 점수 계산 + 추천 이유 생성.
import math
from datetime import datetime, timezone


PREFERRED_TECH_KEYWORDS = {
    "python",
    "javascript",
    "typescript",
    "react",
    "nextjs",
    "vue",
    "fastapi",
    "flask",
    "django",
    "opencv",
    "mediapipe",
    "tensorflow",
    "pytorch",
    "machine-learning",
    "computer-vision",
    "pose-estimation",
    "human-pose-estimation",
    "posture-correction",
}


def _safe_lower(value: str | None) -> str:
    return value.lower() if value else ""


def _get_searchable_text(repo: dict) -> str:

    name = repo.get("name") or ""
    description = repo.get("description") or ""
    language = repo.get("language") or ""
    topics = " ".join(repo.get("topics") or [])

    return f"{name} {description} {language} {topics}".lower()


def _calculate_relevance_score(repo: dict, keywords: list[str]) -> tuple[float, list[str]]:

    if not keywords:
        return 0.0, []

    searchable_text = _get_searchable_text(repo)

    matched_keywords = [
        keyword for keyword in keywords
        if keyword.lower() in searchable_text
    ]

    relevance_score = (len(matched_keywords) / len(keywords)) * 55
    relevance_score = min(relevance_score, 55)

    return relevance_score, matched_keywords


def _calculate_quality_score(repo: dict) -> float:

    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)

    star_score = min(math.log10(stars + 1) * 4, 10)
    fork_score = min(math.log10(forks + 1) * 2.5, 5)

    return min(star_score + fork_score, 15)


def _calculate_recency_score(repo: dict) -> float:

    updated_at = repo.get("updatedAt")

    if not updated_at:
        return 0.0

    try:
        updated_datetime = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except ValueError:
        return 0.0

    now = datetime.now(timezone.utc)
    age_days = (now - updated_datetime).days

    if age_days <= 180:
        return 20.0
    if age_days <= 365:
        return 15.0
    if age_days <= 730:
        return 8.0

    return 3.0


def _calculate_tech_score(repo: dict) -> float:

    language = _safe_lower(repo.get("language"))
    topics = [topic.lower() for topic in repo.get("topics") or []]

    tech_terms = set(topics)

    if language:
        tech_terms.add(language)

    matched = tech_terms.intersection(PREFERRED_TECH_KEYWORDS)

    return min(len(matched) * 2.5, 10)


def _generate_reason(repo: dict, matched_keywords: list[str]) -> str:

    name = repo.get("name", "해당 레포")
    language = repo.get("language") or "주요 언어 정보 없음"
    stars = repo.get("stars", 0)

    if matched_keywords:
        keyword_text = ", ".join(matched_keywords[:4])
        return (
            f"{name}는 입력된 아이디어와 관련된 키워드({keyword_text})가 "
            f"레포 이름, 설명 또는 topics와 매칭되어 추천합니다. "
            f"{language} 기반이며 star {stars}개를 보유해 참고하기 좋습니다."
        )

    return (
        f"{name}는 입력된 아이디어와 유사한 기능을 구현한 레포지토리로 판단됩니다. "
        f"{language} 기반이며 star {stars}개를 보유해 참고할 만합니다."
    )


def score_repository(repo: dict, keywords: list[str]) -> dict:

    relevance_score, matched_keywords = _calculate_relevance_score(repo, keywords)
    quality_score = _calculate_quality_score(repo)
    recency_score = _calculate_recency_score(repo)
    tech_score = _calculate_tech_score(repo)

    total_score = relevance_score + quality_score + recency_score + tech_score
    total_score = round(min(total_score, 100), 2)

    scored_repo = repo.copy()
    scored_repo["score"] = total_score
    scored_repo["reason"] = _generate_reason(repo, matched_keywords)
    scored_repo["matchedKeywords"] = matched_keywords

    return scored_repo


def rank_repositories(repositories: list[dict], keywords: list[str]) -> list[dict]:

    scored_repositories = [
        score_repository(repo, keywords)
        for repo in repositories
    ]

    return sorted(
        scored_repositories,
        key=lambda repo: repo.get("score", 0),
        reverse=True,
    )