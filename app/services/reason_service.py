def _get_retrieved_chunk_summary(repo: dict) -> str:
    """
    RAG 검색으로 찾은 README chunk 일부를 추천 이유에 넣기 위해 정리한다.
    """
    retrieved_chunks = repo.get("retrievedChunks") or []

    if not retrieved_chunks:
        return ""

    best_chunk = retrieved_chunks[0]
    text = best_chunk.get("text") or ""
    similarity = best_chunk.get("similarity", 0.0)

    cleaned_text = " ".join(text.split())

    if len(cleaned_text) > 180:
        cleaned_text = cleaned_text[:180] + "..."

    return f"README에서 유사도 {similarity}로 '{cleaned_text}' 내용이 검색되었습니다."


def generate_recommendation_reason(repo: dict, keywords: list[str]) -> str:
    """
    추천 이유를 생성한다.
    RAG 검색 결과가 있으면 실제 검색된 README chunk 내용을 근거로 사용한다.
    """
    name = repo.get("name") or "해당 레포지토리"
    language = repo.get("language") or "주요 언어 정보 없음"
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)
    rag_score = repo.get("ragScore", 0.0)

    matched_keywords = repo.get("matchedKeywords") or []
    matched_fields = repo.get("matchedFields") or []

    keyword_text = ", ".join(matched_keywords[:5])
    retrieved_chunk_summary = _get_retrieved_chunk_summary(repo)

    if retrieved_chunk_summary:
        return (
            f"{name}는 사용자의 아이디어와 의미적으로 유사한 README 내용이 검색되어 추천합니다. "
            f"{retrieved_chunk_summary} "
            f"{language} 기반이며, star {stars}개와 fork {forks}개를 보유하고 있습니다. "
            f"RAG 유사도 점수는 {rag_score}점입니다."
        )

    evidence_parts = []

    if "metadata" in matched_fields:
        evidence_parts.append("레포지토리 이름, 설명 또는 topics")

    if "readme" in matched_fields:
        evidence_parts.append("README 키워드")

    evidence_text = "와 ".join(evidence_parts)

    if keyword_text and evidence_text:
        return (
            f"{name}는 입력된 아이디어와 관련된 키워드({keyword_text})가 "
            f"{evidence_text}에서 확인되어 추천합니다. "
            f"{language} 기반이며, star {stars}개와 fork {forks}개를 보유하고 있습니다."
        )

    if keyword_text:
        return (
            f"{name}는 입력된 아이디어와 관련된 키워드({keyword_text})가 확인되어 추천합니다. "
            f"{language} 기반이며, star {stars}개와 fork {forks}개를 보유하고 있습니다."
        )

    return (
        f"{name}는 GitHub 검색 결과와 기본 품질 지표를 기준으로 선택된 레포지토리입니다. "
        f"{language} 기반이며, star {stars}개를 보유하고 있습니다."
    )