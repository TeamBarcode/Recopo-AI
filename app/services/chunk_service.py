from app.core.config import settings


def clean_readme_text(text: str) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def split_text_into_chunks(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
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


def _build_chunk_text(repo: dict, readme_chunk: str) -> str:
    topics = repo.get("topics") or []

    return f"""
Repository name: {repo.get("name") or ""}
Full name: {repo.get("fullName") or ""}
Description: {repo.get("description") or ""}
Language: {repo.get("language") or ""}
Topics: {" ".join(topics)}
README:
{readme_chunk}
""".strip()


def build_repository_chunks(repo: dict) -> list[dict]:
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
                "text": _build_chunk_text(repo, chunk),
            }
        )

    return repository_chunks


def build_all_repository_chunks(repositories: list[dict]) -> list[dict]:
    all_chunks = []

    for repo in repositories:
        all_chunks.extend(build_repository_chunks(repo))

    return all_chunks