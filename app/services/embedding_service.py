from sentence_transformers import SentenceTransformer

from app.core.config import settings


_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    embedding 모델을 한 번만 로드해서 재사용한다.
    첫 실행 때는 모델 다운로드 때문에 시간이 걸릴 수 있다.
    """
    global _model

    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    return _model


def embed_text(text: str) -> list[float]:
    """
    하나의 텍스트를 embedding vector로 변환한다.
    """
    model = get_embedding_model()

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    여러 텍스트를 embedding vector 목록으로 변환한다.
    """
    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()