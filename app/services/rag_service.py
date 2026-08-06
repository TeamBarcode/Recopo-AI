import math
from datetime import datetime, timezone

from app.core.config import settings
from app.services.query_service import expand_query_with_keywords
from app.services.vector_store_service import search_similar_chunks


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


def _build_query_text(title: str, content: str) -> str:
    """
    사용자 입력에 keyword 확장을 적용한다.
    """
    return expand_query_with_keywords(title, content).strip()


def _group_chunks_by_repository(similar_chunks: list[dict]) -> dict[int, dict]:
    """
    chunk 검색 결과를 repository 단위로 묶는다.
    """
    grouped: dict[int, dict] = {}

    for chunk in similar_chunks:
        repository_id = chunk.get("repositoryId")

        if repository_id is None:
            continue

        if repository_id not in grouped:
            grouped[repository_id] = {
                "repositoryId": repository_id,
                "name": chunk.get("name"),
                "fullName": chunk.get("fullName"),
                "url": chunk.get("url"),
                "description": chunk.get("description"),
                "language": chunk.get("language"),
                "topics": chunk.get("topics") or [],
                "stars": chunk.get("stars", 0),
                "forks": chunk.get("forks", 0),
                "updatedAt": chunk.get("updatedAt"),
                "bestSimilarity": chunk.get("similarity", 0.0),
                "similaritySum": 0.0,
                "retrievedChunks": [],
            }

        grouped_repo = grouped[repository_id]
        similarity = chunk.get("similarity", 0.0)

        grouped_repo["retrievedChunks"].append(chunk)
        grouped_repo["similaritySum"] += similarity

        if similarity > grouped_repo["bestSimilarity"]:
            grouped_repo["bestSimilarity"] = similarity

    return grouped


def _calculate_rag_similarity_score(grouped_repo: dict) -> float:
    """
    README chunk 유사도 점수.
    """
    best_similarity = grouped_repo.get("bestSimilarity", 0.0)
    similarity_sum = grouped_repo.get("similaritySum", 0.0)
    matched_chunk_count = len(grouped_repo.get("retrievedChunks", []))

    if matched_chunk_count == 0:
        return 0.0

    average_similarity = similarity_sum / matched_chunk_count
    chunk_bonus = min(matched_chunk_count * 2, 10)

    score = (best_similarity * 65) + (average_similarity * 25) + chunk_bonus

    return round(min(score, 100), 2)


def _calculate_quality_score(repo: dict) -> float:
    """
    stars, forks 기반 품질 점수.
    """
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)

    star_score = min(math.log10(stars + 1) * 4, 10)
    fork_score = min(math.log10(forks + 1) * 2.5, 5)

    return round(min(star_score + fork_score, 15), 2)


def _calculate_recency_score(repo: dict) -> float:
    """
    최근 업데이트 점수.
    """
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
    """
    language, topics 기반 기술 점수.
    """
    language = (repo.get("language") or "").lower()
    topics = [topic.lower() for topic in repo.get("topics") or []]

    tech_terms = set(topics)

    if language:
        tech_terms.add(language)

    matched_terms = tech_terms.intersection(PREFERRED_TECH_KEYWORDS)

    return round(min(len(matched_terms) * 2.5, 10), 2)


def _calculate_final_score(repo: dict) -> float:
    """
    최종 추천 점수.
    """
    rag_score = repo.get("ragScore", 0.0)
    quality_score = _calculate_quality_score(repo)
    recency_score = _calculate_recency_score(repo)
    tech_score = _calculate_tech_score(repo)

    final_score = (
        rag_score * 0.65
        + tech_score * 1.3
        + recency_score * 0.8
        + quality_score * 0.5
    )

    return round(min(final_score, 100), 2)


def recommend_repositories_with_rag(
    title: str,
    content: str,
    top_k: int | None = None,
) -> list[dict]:
    """
    Vector DB에서 유사 README chunk를 찾고 repository 후보로 변환한다.
    """
    query_text = _build_query_text(title, content)

    similar_chunks = search_similar_chunks(
        query=query_text,
        top_k=top_k,
    )

    if not similar_chunks:
        return []

    grouped_repositories = _group_chunks_by_repository(similar_chunks)

    repositories = []

    for grouped_repo in grouped_repositories.values():
        best_similarity = grouped_repo.get("bestSimilarity", 0.0)

        if best_similarity < settings.RAG_MIN_SIMILARITY:
            continue

        repo = grouped_repo.copy()
        repo["ragScore"] = _calculate_rag_similarity_score(grouped_repo)
        repo["score"] = _calculate_final_score(repo)
        repo["source"] = "rag"

        repositories.append(repo)

    return sorted(
        repositories,
        key=lambda repo: repo.get("score", 0.0),
        reverse=True,
    )