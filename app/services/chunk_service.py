from app.core.config import settings


def clean_readme_text(text: str) -> str:
    """
    README 텍스트에서 불필요한 공백과 빈 줄을 정리한다.
    """
    if not text:
        return ""

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def split_text_into_chunks(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """
    긴 README 텍스트를 일정 길이의 chunk로 나눈다.

    예:
    README 전체 4000자
    → 800자 단위 chunk
    → 앞뒤 chunk가 120자 정도 겹치게 분리
    """
    chunk_size = settings.README_CHUNK_SIZE if chunk_size is None else chunk_size
    overlap = settings.README_CHUNK_OVERLAP if overlap is None else overlap

    cleaned_text = clean_readme_text(text)

    if not cleaned_text:
        return []

    if chunk_size <= 0:
        return [cleaned_text]

    if overlap >= chunk_size:
        overlap = 0

    chunks = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = start + chunk_size
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def build_repository_chunks(repo: dict) -> list[dict]:
    """
    하나의 repository README를 chunk 목록으로 변환한다.
    각 chunk에는 어떤 repository에서 나온 내용인지 metadata를 같이 붙인다.
    """
    readme = repo.get("readme") or ""
    chunks = split_text_into_chunks(readme)

    repository_chunks = []

    for index, chunk in enumerate(chunks):
        repository_chunks.append(
            {
                "repositoryId": repo.get("repositoryId"),
                "name": repo.get("name"),
                "fullName": repo.get("fullName"),
                "url": repo.get("url"),
                "description": repo.get("description") or "",
                "language": repo.get("language") or "",
                "topics": repo.get("topics") or [],
                "stars": repo.get("stars", 0),
                "forks": repo.get("forks", 0),
                "updatedAt": repo.get("updatedAt") or "",
                "chunkIndex": index,
                "text": chunk,
            }
        )

    return repository_chunks


def build_all_repository_chunks(repositories: list[dict]) -> list[dict]:
    """
    여러 repository의 README를 전부 chunk로 변환한다.
    """
    all_chunks = []

    for repo in repositories:
        all_chunks.extend(build_repository_chunks(repo))

    return all_chunks