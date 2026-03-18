from pathlib import Path

from dotenv import load_dotenv

from Translator import Translator
from tests.TestUtil import build_absolute_path
from llm.ChatOpenAI import ChatOpenAI
from local_adapter.LocalDataAccessor import LocalDataAccessor

# Load .env file if it exists (for local development)
# In CI, environment variables are set via AWS Parameter Store
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

class TestTranslator:

    def test_translate_to_german_for_english_text(self):
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)
        translator = Translator(llm=llm, temperature=0)

        result = translator.translate_to_german_if_needed("This is a test string that should be translated to German.")

        assert result.original_language.name.lower() == "english"
        assert result.original_language.iso_code == "en"
        assert "übersetzt" in result.german_translation
        assert result.original == "This is a test string that should be translated to German."

    def test_no_translation_for_german_text(self):
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)
        translator = Translator(llm=llm, temperature=0)

        result = translator.translate_to_german_if_needed("Das ist ein einfacher Test")

        assert result.original_language.name.lower() == "german"
        assert result.original_language.iso_code == "de"
        assert result.german_translation == "Das ist ein einfacher Test"
        assert result.original == "Das ist ein einfacher Test"