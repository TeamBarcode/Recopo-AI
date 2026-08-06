FEATURE_KEYWORD_MAP = {
    "pose": "자세 인식",
    "posture": "자세 교정",
    "correction": "교정 기능",
    "rep counter": "운동 반복 횟수 측정",
    "repetition": "반복 동작 분석",
    "exercise": "운동 동작 분석",
    "fitness": "운동 보조 기능",
    "computer vision": "컴퓨터 비전",
    "opencv": "OpenCV 기반 영상 처리",
    "mediapipe": "MediaPipe 기반 자세 추정",
    "camera": "카메라 기반 분석",
    "webcam": "웹캠 기반 분석",
    "real-time": "실시간 처리",
    "realtime": "실시간 처리",
    "recommendation": "추천 기능",
    "recommender": "추천 시스템",
    "chatbot": "챗봇 기능",
    "rag": "문서 검색 기반 답변",
    "llm": "AI 답변 생성",
    "expense": "비용 관리",
    "split": "정산 기능",
    "settlement": "정산 기능",
    "movie": "영화 추천",
    "plant": "식물 분석",
    "disease": "질병 탐지",
}


def _clean_text(text: str) -> str:
    if not text:
        return ""

    return " ".join(text.split())


def _format_topics(topics: list[str], max_count: int = 4) -> str:
    if not topics:
        return ""

    return ", ".join(topics[:max_count])


def _get_retrieved_text(repo: dict, max_chunks: int = 2) -> str:

    retrieved_chunks = repo.get("retrievedChunks") or []

    texts = []
    for chunk in retrieved_chunks[:max_chunks]:
        text = _clean_text(chunk.get("text") or "")
        if text:
            texts.append(text)

    return " ".join(texts)


def _extract_feature_keywords(repo: dict, max_count: int = 4) -> list[str]:

    description = repo.get("description") or ""
    topics = " ".join(repo.get("topics") or [])
    readme_text = _get_retrieved_text(repo)

    source_text = f"{description} {topics} {readme_text}".lower()

    features = []

    for keyword, feature_name in FEATURE_KEYWORD_MAP.items():
        if keyword in source_text and feature_name not in features:
            features.append(feature_name)

        if len(features) >= max_count:
            break

    return features


def _build_intro_reason(repo: dict) -> str:
    name = repo.get("name") or "이 레포지토리"
    description = repo.get("description") or ""

    if description:
        return (
            f"{name}는 '{description}'와 관련된 레포지토리로, "
            f"입력한 프로젝트 아이디어와 기능적으로 유사해 추천되었습니다."
        )

    return (
        f"{name}는 입력한 프로젝트 아이디어와 관련된 구현 내용을 포함하고 있어 "
        f"참고용 레포지토리로 추천되었습니다."
    )


def _build_feature_reason(repo: dict) -> str:
    features = _extract_feature_keywords(repo)

    if not features:
        return (
            "README와 레포지토리 정보를 기준으로 아이디어 구현에 참고할 수 있는 "
            "구현 흐름이 확인되었습니다."
        )

    feature_text = ", ".join(features)

    return (
        f"README와 레포지토리 정보에서 {feature_text} 관련 내용이 확인되어 "
        f"서비스의 핵심 기능을 설계할 때 참고하기 좋습니다."
    )


def _build_tech_reason(repo: dict) -> str:
    language = repo.get("language")
    topics = repo.get("topics") or []
    topic_text = _format_topics(topics)

    if language and topic_text:
        return (
            f"또한 {language} 기반이며 {topic_text} 관련 topic이 포함되어 있어 "
            f"기술 스택과 구현 방식을 함께 확인할 수 있습니다."
        )

    if language:
        if language.lower() == "jupyter notebook":
            return (
                "또한 Jupyter Notebook 기반으로 구성되어 있어 "
                "데이터 처리나 모델 실험 흐름을 단계별로 참고하기 좋습니다."
            )

        return (
            f"또한 {language} 기반으로 구현되어 있어 "
            f"관련 기술 스택의 코드 구조를 참고할 수 있습니다."
        )

    if topic_text:
        return (
            f"또한 {topic_text} 관련 topic이 포함되어 있어 "
            f"프로젝트 구현 방향을 잡는 데 도움이 됩니다."
        )

    return ""


def _build_update_reason(repo: dict) -> str:
    updated_at = repo.get("updatedAt") or ""

    if not updated_at:
        return ""

    return (
        f"최근 업데이트일은 {updated_at[:10]}로 확인되어, "
        f"아이디어 구현 참고용으로 활용할 수 있습니다."
    )


def generate_recommendation_reason(
    repo: dict,
    keywords: list[str],
    title: str = "",
    content: str = "",
) -> str:

    reason_parts = [
        _build_intro_reason(repo),
        _build_feature_reason(repo),
    ]

    tech_reason = _build_tech_reason(repo)
    update_reason = _build_update_reason(repo)

    if tech_reason:
        reason_parts.append(tech_reason)

    if update_reason:
        reason_parts.append(update_reason)

    return " ".join(reason_parts)
