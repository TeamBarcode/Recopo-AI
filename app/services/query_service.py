from dataclasses import dataclass

from app.core.config import settings
from app.services.translation_service import (
    TranslationError,
    TranslationService,
)


@dataclass(frozen=True)
class SearchQueryResult:
    original_query: str
    search_query: str
    translated: bool


class QueryService:
    def __init__(
        self,
        translation_service: TranslationService,
    ) -> None:
        self.translation_service = translation_service

    def build_search_query(
        self,
        title: str,
        content: str,
    ) -> SearchQueryResult:
        original_query = " ".join(
            f"{title} {content}".split()
        )

        if not original_query:
            raise ValueError("검색어가 비어 있습니다.")

        try:
            translated_query = (
                self.translation_service.translate_to_english(
                    original_query
                )
            )

            return SearchQueryResult(
                original_query=original_query,
                search_query=translated_query,
                translated=translated_query != original_query,
            )

        except TranslationError:
            return SearchQueryResult(
                original_query=original_query,
                search_query=original_query,
                translated=False,
            )


translation_service = TranslationService(
    api_key=settings.DEEPL_API_KEY,
    api_url=settings.DEEPL_API_URL,
    timeout_seconds=settings.TRANSLATION_TIMEOUT_SECONDS,
    max_chars=settings.TRANSLATION_MAX_CHARS,
)

query_service = QueryService(
    translation_service=translation_service,
)