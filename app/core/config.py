import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    # GitHub API
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_API_URL: str = os.getenv(
        "GITHUB_API_URL",
        "https://api.github.com",
    )
    GITHUB_TIMEOUT: int = int(
        os.getenv("GITHUB_TIMEOUT", "10")
    )

    GITHUB_SEARCH_PER_PAGE: int = int(
        os.getenv("GITHUB_SEARCH_PER_PAGE", "30")
    )
    GITHUB_README_CANDIDATE_LIMIT: int = int(
        os.getenv("GITHUB_README_CANDIDATE_LIMIT", "10")
    )
    GITHUB_README_MAX_CHARS: int = int(
        os.getenv("GITHUB_README_MAX_CHARS", "4000")
    )

    MIN_REPOSITORY_STARS: int = int(
        os.getenv("MIN_REPOSITORY_STARS", "5")
    )

    # Translation API
    DEEPL_API_KEY: str = os.getenv(
        "DEEPL_API_KEY",
        "",
    )
    DEEPL_API_URL: str = os.getenv(
        "DEEPL_API_URL",
        "https://api-free.deepl.com",
    )
    TRANSLATION_TIMEOUT_SECONDS: float = float(
        os.getenv("TRANSLATION_TIMEOUT_SECONDS", "3.0")
    )
    TRANSLATION_MAX_CHARS: int = int(
        os.getenv("TRANSLATION_MAX_CHARS", "1000")
    )

    # Embedding
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )

    # Repository data
    REPOSITORY_DATA_PATH: str = os.getenv(
        "REPOSITORY_DATA_PATH",
        "data/repositories.json",
    )

    # ChromaDB
    CHROMA_DB_DIR: str = os.getenv(
        "CHROMA_DB_DIR",
        "data/vector_store",
    )

    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "github_readme_chunks",
    )

    # README chunking
    README_CHUNK_SIZE: int = int(
        os.getenv("README_CHUNK_SIZE", "800")
    )
    README_CHUNK_OVERLAP: int = int(
        os.getenv("README_CHUNK_OVERLAP", "120")
    )

    # RAG retrieval
    RAG_TOP_K_CHUNKS: int = int(
        os.getenv("RAG_TOP_K_CHUNKS", "10")
    )
    RAG_MIN_SIMILARITY: float = float(
        os.getenv("RAG_MIN_SIMILARITY", "0.55")
    )


settings = Settings()