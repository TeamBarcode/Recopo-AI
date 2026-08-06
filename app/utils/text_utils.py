import re


def normalize_text(text: str) -> str:
    

    
    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ.-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def combine_title_content(title: str, content: str) -> str:
    

    
    combined = f"{title} {content}"
    return normalize_text(combined)
