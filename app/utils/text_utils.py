# 검색하기 좋은 문자열로 정리.
import re


def normalize_text(text: str) -> str:
    
    #입력 텍스트의 줄바꿈, 특수문자, 중복 공백을 정리
    
    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ.-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def combine_title_content(title: str, content: str) -> str:
    
    #title과 content를 하나의 검색용 문장으로 합치기
    
    combined = f"{title} {content}"
    return normalize_text(combined)