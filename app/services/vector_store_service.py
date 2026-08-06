import chromadb

from app.core.config import settings
from app.services.embedding_service import embed_text, embed_texts


def get_chroma_client():
    """
    로컬 디스크에 저장되는 ChromaDB client를 생성한다.
    """
    return chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)


def get_collection():
    """
    README chunk 저장용 collection을 가져온다.
    없으면 새로 생성한다.
    """
    client = get_chroma_client()

    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection() -> None:
    """
    기존 collection을 삭제하고 새 collection을 만든다.
    build_vector_store.py 실행 시 중복 저장을 막기 위해 사용한다.
    """
    client = get_chroma_client()

    try:
        client.delete_collection(settings.CHROMA_COLLECTION_NAME)
    except Exception:
        pass

    client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _topics_to_string(topics: list[str]) -> str:
    """
    ChromaDB metadata에는 list 대신 문자열로 topics를 저장한다.
    """
    return ",".join(topics or [])


def _string_to_topics(topics: str) -> list[str]:
    """
    문자열로 저장된 topics를 다시 list로 변환한다.
    """
    if not topics:
        return []

    return [topic for topic in topics.split(",") if topic]


def add_chunks_to_vector_store(chunks: list[dict]) -> int:
    """
    README chunk들을 embedding으로 변환한 뒤 ChromaDB에 저장한다.
    """
    if not chunks:
        return 0

    collection = get_collection()

    documents = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(documents)

    ids = []
    metadatas = []

    for chunk in chunks:
        repository_id = chunk.get("repositoryId")
        chunk_index = chunk.get("chunkIndex")

        if repository_id is None:
            continue

        ids.append(f"{repository_id}-{chunk_index}")

        metadatas.append(
            {
                "repositoryId": int(repository_id or 0),
                "name": chunk.get("name") or "",
                "fullName": chunk.get("fullName") or "",
                "url": chunk.get("url") or "",
                "description": chunk.get("description") or "",
                "language": chunk.get("language") or "",
                "topics": _topics_to_string(chunk.get("topics") or []),
                "stars": int(chunk.get("stars") or 0),
                "forks": int(chunk.get("forks") or 0),
                "updatedAt": chunk.get("updatedAt") or "",
                "chunkIndex": int(chunk_index or 0),
            }
        )

    if not ids:
        return 0

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(ids)


def search_similar_chunks(query: str, top_k: int | None = None) -> list[dict]:
    """
    사용자 입력과 의미적으로 유사한 README chunk를 Vector DB에서 검색한다.
    """
    top_k = settings.RAG_TOP_K_CHUNKS if top_k is None else top_k

    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_text(query)

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    similar_chunks = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        similarity = 1 - float(distance)

        similar_chunks.append(
            {
                "repositoryId": metadata.get("repositoryId"),
                "name": metadata.get("name"),
                "fullName": metadata.get("fullName"),
                "url": metadata.get("url"),
                "description": metadata.get("description"),
                "language": metadata.get("language"),
                "topics": _string_to_topics(metadata.get("topics", "")),
                "stars": metadata.get("stars", 0),
                "forks": metadata.get("forks", 0),
                "updatedAt": metadata.get("updatedAt"),
                "chunkIndex": metadata.get("chunkIndex"),
                "text": document,
                "similarity": round(similarity, 4),
            }
        )

    return similar_chunks