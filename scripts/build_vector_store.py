import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings
from app.services.chunk_service import build_all_repository_chunks
from app.services.vector_store_service import (
    add_chunks_to_vector_store,
    reset_collection,
)


def load_repositories() -> list[dict]:
    """
    collect_repositories.py가 저장한 data/repositories.json을 읽는다.
    """
    data_path = Path(settings.REPOSITORY_DATA_PATH)

    if not data_path.exists():
        raise FileNotFoundError(
            f"{data_path} 파일이 없습니다. 먼저 collect_repositories.py를 실행하세요."
        )

    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    repositories = load_repositories()

    print(f"[레포 로드] {len(repositories)}개")

    chunks = build_all_repository_chunks(repositories)

    print(f"[chunk 생성] {len(chunks)}개")

    reset_collection()

    inserted_count = add_chunks_to_vector_store(chunks)

    print(f"[Vector DB 저장 완료] {inserted_count}개 chunk 저장")