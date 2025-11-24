import json
import os
from pathlib import Path

from dotenv import load_dotenv
from memory.MemoryProvider import MemoryProvider
from pinecone_db.PineconeDbRepository import PineconeDbRepository
from SupportRequestHandler import SupportRequestHandler
from UserRequest import UserRequest
from tests.ModelConfiguration import ModelConfiguration

# Load .env from the tests directory
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

model_configurations = [
  ModelConfiguration(model_name="gpt-4.1-mini", temperature=0.2),
  ModelConfiguration(model_name="gemini-2.5-flash", temperature=0.2)
]

class TestReferenceQuestions:
  def setup_method(self):
    os.environ["USE_CHECKPOINTER_IN_MEMORY"] = "True"
    os.environ["LANGSMITH_TRACING"] = "False"
    os.environ["GEMINI_ENABLED"] = "False"
    os.environ["OPENAI_ENABLED"] = "False"

    vector_db_repository = PineconeDbRepository()
    memory_provider = MemoryProvider()
    self.support_request_handler = SupportRequestHandler(
        memory_provider=memory_provider, 
        vector_db_repository=vector_db_repository
    )

  def test_question_activating_waitlist_participants(self):
    self._execute_test_with_model_configurations("activating-waitlist-participants")
    
  def test_question_bulk_import_participants(self):
    self._execute_test_with_model_configurations("bulk-import-participants")    

  def test_question_changing_team_size(self):
    self._execute_test_with_model_configurations("changing-team-size")

  def test_question_emails_not_sending(self):
    self._execute_test_with_model_configurations("emails-not-sending")

  def test_question_export_participants_to_excel(self):
    self._execute_test_with_model_configurations("export-participants-to-excel")

  def test_question_guest_registration_errors(self):
    self._execute_test_with_model_configurations("guest-registration-errors")

  def test_question_missing_confirmation_email(self):
    self._execute_test_with_model_configurations("missing-confirmation-email")

  def test_question_modify_gender_distribution_setting(self):
    self._execute_test_with_model_configurations("modify-gender-distribution-setting")

  def test_question_recover_admin_link(self):
    self._execute_test_with_model_configurations("recover-admin-link")

  def test_question_route_calculation_algorithm(self):
    self._execute_test_with_model_configurations("route-calculation-algorithm")


  def _execute_test_with_model_configurations(self, question_filename_pure: str):
    for model_config in model_configurations:
      self._setup_environment_for_model_configuration(model_config)
      
      question_text = self._read_question_file(f"{question_filename_pure}.txt")
      user_request = UserRequest(question=question_text, thread_id=question_filename_pure)

      response = self.support_request_handler.process_user_request(user_request)
      body = response["body"]
      answer = json.loads(body)['answer']

      self._write_answer_file(question_filename_pure, answer, model_config.model_name)


  def _setup_environment_for_model_configuration(self, model_config: ModelConfiguration):
    if "gemini" in model_config.model_name.lower():
      os.environ["GEMINI_ENABLED"] = "True"
      os.environ["OPENAI_ENABLED"] = "False"
      os.environ["GEMINI_MODEL"] = model_config.model_name
      os.environ["GEMINI_TEMPERATURE"] = str(model_config.temperature)
    else:
      os.environ["GEMINI_ENABLED"] = "False"
      os.environ["OPENAI_ENABLED"] = "True"
      os.environ["OPENAI_MODEL"] = model_config.model_name
      os.environ["OPENAI_TEMPERATURE"] = str(model_config.temperature)


  def _read_question_file(self, question_filename: str) -> str:
    test_dir = Path(__file__).parent
    reference_questions_dir = test_dir / "reference_questions"
    # Read the question file
    question_file = reference_questions_dir / question_filename
    return question_file.read_text(encoding="utf-8")


  def _write_answer_file(self, answer_filename: str, answer_text: str, llm_model: str):
    test_dir = Path(__file__).parent
    reference_questions_dir = test_dir / "reference_questions"
    answers_dir = reference_questions_dir / "reference-answers"
    answer_file = answers_dir / f"{answer_filename}-{llm_model}.txt"
    answer_file.write_text(answer_text, encoding="utf-8")
