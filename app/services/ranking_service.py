# 후보 레포마다 점수 계산 + 추천 이유 생성
"""
    점수 구성:
    - 메타데이터 관련성: 35점
    - README 관련성: 25점
    - 품질: 15점
    - 최신성: 15점
    - 기술스택: 10점
"""
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
    "deep-learning",
    "computer-vision",
    "pose-estimation",
    "human-pose-estimation",
    "posture-correction",
    "webcam",
    "real-time",
}


def _safe_lower(value: str | None) -> str:
    return value.lower() if value else ""


def _get_metadata_text(repo: dict) -> str:

    name = repo.get("name") or ""
    description = repo.get("description") or ""
    language = repo.get("language") or ""
    topics = " ".join(repo.get("topics") or [])

    return f"{name} {description} {language} {topics}".lower()


def _get_readme_text(repo: dict) -> str:

    return (repo.get("readme") or "").lower()


def _get_matched_keywords(keywords: list[str], text: str) -> list[str]:

    matched_keywords = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        if keyword_lower in text and keyword_lower not in matched_keywords:
            matched_keywords.append(keyword_lower)

    return matched_keywords


def _calculate_text_relevance_score(
    keywords: list[str],
    text: str,
    max_score: float,
) -> tuple[float, list[str]]:

    if not keywords or not text:
        return 0.0, []

    matched_keywords = _get_matched_keywords(keywords, text)

    score = (len(matched_keywords) / len(keywords)) * max_score
    score = min(score, max_score)

    return score, matched_keywords


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
        return 15.0

    if age_days <= 365:
        return 11.0

    if age_days <= 730:
        return 6.0

    return 2.0


def _calculate_tech_score(repo: dict) -> float:

    language = _safe_lower(repo.get("language"))
    topics = [topic.lower() for topic in repo.get("topics") or []]

    tech_terms = set(topics)

    if language:
        tech_terms.add(language)

    matched = tech_terms.intersection(PREFERRED_TECH_KEYWORDS)

    return min(len(matched) * 2.5, 10)


def score_repository(
    repo: dict,
    keywords: list[str],
    use_readme: bool = True,
) -> dict:

    metadata_text = _get_metadata_text(repo)
    readme_text = _get_readme_text(repo)

    metadata_score, metadata_matches = _calculate_text_relevance_score(
        keywords=keywords,
        text=metadata_text,
        max_score=35,
    )

    readme_score = 0.0
    readme_matches: list[str] = []

    if use_readme:
        readme_score, readme_matches = _calculate_text_relevance_score(
            keywords=keywords,
            text=readme_text,
            max_score=25,
        )

    quality_score = _calculate_quality_score(repo)
    recency_score = _calculate_recency_score(repo)
    tech_score = _calculate_tech_score(repo)

    total_score = (
        metadata_score
        + readme_score
        + quality_score
        + recency_score
        + tech_score
    )

    matched_keywords = []

    for keyword in metadata_matches + readme_matches:
        if keyword not in matched_keywords:
            matched_keywords.append(keyword)

    matched_fields = []

    if metadata_matches:
        matched_fields.append("metadata")

    if readme_matches:
        matched_fields.append("readme")

    scored_repo = repo.copy()
    scored_repo["score"] = round(min(total_score, 100), 2)
    scored_repo["matchedKeywords"] = matched_keywords
    scored_repo["matchedFields"] = matched_fields
    scored_repo["scoreDetails"] = {
        "metadataScore": round(metadata_score, 2),
        "readmeScore": round(readme_score, 2),
        "qualityScore": round(quality_score, 2),
        "recencyScore": round(recency_score, 2),
        "techScore": round(tech_score, 2),
    }

    return scored_repo


def rank_repositories(
    repositories: list[dict],
    keywords: list[str],
    use_readme: bool = True,
) -> list[dict]:

    scored_repositories = [
        score_repository(repo, keywords, use_readme=use_readme)
        for repo in repositories
    ]

    return sorted(
        scored_repositories,
        key=lambda repo: repo.get("score", 0),
        reverse=True,
    )