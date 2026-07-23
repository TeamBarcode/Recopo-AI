def generate_recommendation_reason(repo: dict, keywords: list[str]) -> str:

    name = repo.get("name") or "해당 레포지토리"
    language = repo.get("language") or "주요 언어 정보 없음"
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)

    matched_keywords = repo.get("matchedKeywords") or []
    matched_fields = repo.get("matchedFields") or []
    score_details = repo.get("scoreDetails") or {}

    keyword_text = ", ".join(matched_keywords[:5])

    evidence_parts = []

    if "metadata" in matched_fields:
        evidence_parts.append("레포지토리 이름, 설명 또는 topics")

    if "readme" in matched_fields:
        evidence_parts.append("README 내용")

    evidence_text = "와 ".join(evidence_parts)

    if keyword_text and evidence_text:
        return (
            f"{name}는 입력된 아이디어와 관련된 키워드({keyword_text})가 "
            f"{evidence_text}에서 확인되어 추천합니다. "
            f"{language} 기반이며, star {stars}개와 fork {forks}개를 보유하고 있어 "
            f"구현 참고용 레포지토리로 적합합니다."
        )

    if keyword_text:
        return (
            f"{name}는 입력된 아이디어와 관련된 키워드({keyword_text})가 확인되어 추천합니다. "
            f"{language} 기반이며, star {stars}개와 fork {forks}개를 보유하고 있습니다."
        )

    metadata_score = score_details.get("metadataScore", 0)
    readme_score = score_details.get("readmeScore", 0)

    if metadata_score > 0 or readme_score > 0:
        return (
            f"{name}는 입력된 아이디어와 기능적으로 유사한 레포지토리로 판단되어 추천합니다. "
            f"{language} 기반이며, 기존 구현 구조를 참고하기 좋습니다."
        )

    return (
        f"{name}는 GitHub 검색 결과와 기본 품질 지표를 기준으로 선택된 레포지토리입니다. "
        f"{language} 기반이며, star {stars}개를 보유하고 있습니다."
    )