import re

import requests


class TranslationError(RuntimeError):
    pass


class TranslationService:
    def __init__(
        self,
        api_key: str,
        api_url: str,
        timeout_seconds: float,
        max_chars: int,
    ) -> None:
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_chars = max_chars

    def translate_to_english(self, text: str) -> str:
        text = " ".join(text.split())[: self.max_chars]

        if not text:
            return ""

        if not re.search(r"[가-힣]", text):
            return text

        if not self.api_key:
            raise TranslationError("DEEPL_API_KEY가 없습니다.")

        try:
            response = requests.post(
                f"{self.api_url}/v2/translate",
                headers={
                    "Authorization": f"DeepL-Auth-Key {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text": [text],
                    "source_lang": "KO",
                    "target_lang": "EN-US",
                },
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()
            data = response.json()
            translated_text = data["translations"][0]["text"].strip()

        except (
            requests.RequestException,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as exc:
            raise TranslationError(
                "번역 API 요청에 실패했습니다."
            ) from exc

        if not translated_text:
            raise TranslationError("번역 결과가 비어 있습니다.")

        return translated_text