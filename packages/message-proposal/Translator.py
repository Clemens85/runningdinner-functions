from llm.ChatOpenAI import ChatOpenAI
from DetectedLanguage import DetectedLanguage
from TextTranslation import TextTranslation
from logger.Log import logger

class Translator:
    def __init__(self, llm: ChatOpenAI, model: str = None, temperature: float = 0):
        self.llm = llm
        self.model = model
        self.temperature = temperature

    def translate_to_language(self, text: str, language: DetectedLanguage) -> str:
        translation_prompt = f"""
        Translate the following text which is formatted in Markdown to {language.name}.
        Return only the {language.name} translation and preserve the markdown structure in your translation. 
        Return no further explanations and no further information. 
        Here is the text:\n\n{text}\n\n{language.name} translation:
        """
        translation_response = self.llm.invoke(
            model_override=self.model,
            temperature_override=self.temperature,
            prompt=[
                {"role": "system", "content": "You are a helpful assistant that translates texts to German."},
                {"role": "user", "content": translation_prompt}
            ]
        )
        return translation_response.content.strip()

    def detect_language(self, text: str) -> DetectedLanguage:
        
        text_excerpt = text[:512]  # Use only the first 512 characters for language detection to save costs and speed up the process

        detection_prompt = f"""
        Detect the language of the following text excerpt and return the language code with a dash and then the language name (e.g. 'de - German' for German, 'en - English' for English).
        Return only the language code with the language name. Do not return any explanations or additional information.
        Here is the text:\n\n{text_excerpt}\n\nLanguage code with language name:
        """
        detection_response = self.llm.invoke(
            model_override=self.model,
            temperature_override=self.temperature,
            prompt=[
                {"role": "system", "content": "You are a helpful assistant that detects the language of a given text and returns the corresponding language code with the language name."},
                {"role": "user", "content": detection_prompt}
            ]
        )
        result_str = detection_response.content.strip()
        try:
            code, name = result_str.split("-", 1)
            return DetectedLanguage(iso_code=code.strip(), name=name.strip())
        except Exception as e:
            # In case of any parsing issues, default to German
            logger.error(f"Failed to parse detected language response: {str(e)}. Response was: '{result_str}'. Defaulting to German.")
            return DetectedLanguage(iso_code="de", name="German")

    def translate_to_german_if_needed(self, text: str) -> TextTranslation:
        original_language = self.detect_language(text)
        if original_language.iso_code != "de":
            german_translation = self.translate_to_language(text, DetectedLanguage(iso_code="de", name="German"))
            return TextTranslation(original=text, german_translation=german_translation, original_language=original_language)
        else:
            return TextTranslation(original=text, german_translation=text, original_language=original_language)