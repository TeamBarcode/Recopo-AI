#한글 입력을 GitHub 검색용 영어 키워드로 변환
from app.utils.text_utils import combine_title_content


KEYWORD_MAP = {
    "ai": ["ai", "machine-learning"],
    "인공지능": ["ai", "machine-learning"],
    "머신러닝": ["machine-learning"],
    "딥러닝": ["deep-learning"],
    "추천": ["recommendation", "recommender-system"],
    "영화": ["movie"],
    "음악": ["music"],
    "맛집": ["restaurant"],
    "음식": ["food"],
    "일정": ["schedule", "calendar"],
    "할일": ["todo", "task-management"],
    "투두": ["todo", "task-management"],
    "채팅": ["chat", "chatbot"],
    "챗봇": ["chatbot"],
    "운동": ["fitness", "exercise"],
    "자세": ["pose-estimation", "posture", "human-pose-estimation"],
    "교정": ["posture-correction", "correction"],
    "웹캠": ["webcam", "camera"],
    "카메라": ["camera", "computer-vision"],
    "분석": ["analysis", "computer-vision"],
    "실시간": ["real-time"],
    "웹서비스": ["web-app"],
    "웹": ["web"],
    "앱": ["app"],
    "서비스": ["app"],
    "로그인": ["login", "authentication"],
    "게시판": ["board", "community"],
    "커뮤니티": ["community"],
    "쇼핑": ["shopping", "ecommerce"],
    "결제": ["payment"],
    "지도": ["map"],
    "위치": ["location"],
    "이미지": ["image", "computer-vision"],
    "사진": ["image"],
    "음성": ["speech", "audio"],
    "번역": ["translation"],
    "opencv": ["opencv"],
    "mediapipe": ["mediapipe"],
    "미디어파이프": ["mediapipe"],
    "파이썬": ["python"],
    "리액트": ["react"],
    "스프링": ["spring"],
    "fastapi": ["fastapi"],
}


def extract_keywords(title: str, content: str) -> list[str]:

    text = combine_title_content(title, content)
    text_lower = text.lower()

    keywords: list[str] = []

    for source_word, english_terms in KEYWORD_MAP.items():
        if source_word.lower() in text_lower:
            keywords.extend(english_terms)

    unique_keywords: list[str] = []

    for keyword in keywords:
        normalized_keyword = keyword.strip().lower()

        if normalized_keyword and normalized_keyword not in unique_keywords:
            unique_keywords.append(normalized_keyword)

    if not unique_keywords:
        return ["web", "app", "project"]

    return unique_keywords


def create_search_queries(title: str, content: str) -> list[str]:

    keywords = extract_keywords(title, content)

    main_keywords = keywords[:10]
    core_keywords = keywords[:6]

    queries = [
        f"{' '.join(main_keywords)} in:name,description,readme",
        f"{' '.join(core_keywords)} in:name,description",
        f"{' '.join(core_keywords)} stars:>10",
    ]

    unique_queries: list[str] = []

    for query in queries:
        if query not in unique_queries:
            unique_queries.append(query)

    return unique_queries


def create_search_query(title: str, content: str) -> str:

    return create_search_queries(title, content)[0]