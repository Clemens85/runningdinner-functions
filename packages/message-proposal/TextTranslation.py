from pydantic import BaseModel

from DetectedLanguage import DetectedLanguage


class TextTranslation(BaseModel):
    original: str
    original_language: DetectedLanguage
    german_translation: str
