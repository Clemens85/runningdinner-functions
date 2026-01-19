from pathlib import Path

from dotenv import load_dotenv

from Anonymizer import Anonymizer
from ProposalFileType import ProposalFileType
from TestUtil import build_absolute_path
from llm.ChatOpenAI import ChatOpenAI
from local_adapter.LocalDataAccessor import LocalDataAccessor

# Load .env file if it exists (for local development)
# In CI, environment variables are set via AWS Parameter Store
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

class TestAnonymizer:

    def test_removal_of_pii(self):
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)
        anonymizer = Anonymizer(llm=llm, temperature=0)

        data_accessor = LocalDataAccessor(root_path=build_absolute_path("fixtures"))
        sample_text = data_accessor.load_string(storage_path="input/EVENT_DESCRIPTION/event_1.md")
        assert len(sample_text) > 0

        result = anonymizer.anonymize_personal_data(sample_text, ProposalFileType.EVENT_DESCRIPTION)

        # print out result
        print("Anonymized Result:\n", result)
        assert "clemens" not in result.lower()
        assert "helen" not in result.lower()
        assert "emil" not in result.lower()
        assert "freiburg" not in result.lower()
        assert "fakestr" not in result.lower()
        assert "clemens@example.de" not in result.lower()
        assert "123456789" not in result
        # assert "kandelhof" not in result.lower()
        # assert "dreisam" not in result.lower()
        assert "79098" not in result
        assert "79100" not in result
        assert "79111" not in result
        assert "79112" not in result
        assert "79113" not in result