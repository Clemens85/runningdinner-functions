from pathlib import Path
from dotenv import load_dotenv
import os

from ProposalInputHandler import ProposalInputHandler
from tests.TestUtil import build_absolute_path, ensure_subfolder
from llm.ChatOpenAI import ChatOpenAI
from local_adapter.LocalDataAccessor import LocalDataAccessor
from local_adapter.LocalInMemoryDbRepository import LocalInMemoryDbRepository
from local_adapter.LocalNotificationHandler import LocalNotificationHandler

# Load .env file if it exists (for local development)
# In CI, environment variables are set via AWS Parameter Store
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)


class TestProposalInputHandler:

    def setup_method(self):
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)
        source_bucket = build_absolute_path("fixtures")
        ensure_subfolder(source_bucket, "generated/message/TEAM", True)
        ensure_subfolder(source_bucket, "generated/message/DINNER_ROUTE", True)
        ensure_subfolder(source_bucket, "processed/message/TEAM", True)
        ensure_subfolder(source_bucket, "processed/message/DINNER_ROUTE", True)
        ensure_subfolder(source_bucket, "processed/EVENT_DESCRIPTION", True)

        self.data_accessor = LocalDataAccessor(root_path=source_bucket)
        self.vector_db = LocalInMemoryDbRepository()
        self.notification_handler = LocalNotificationHandler()
        self.proposal_input_handler = ProposalInputHandler(
            data_accessor=self.data_accessor,
            vector_db_repository=self.vector_db,
            llm=self.llm,
            notification_handler=self.notification_handler
        )
        self.source_bucket = source_bucket

    def test_complete_workflow(self):

        # *** REQUEST 1: Process initial event description ***
        self.proposal_input_handler.process_request("input/EVENT_DESCRIPTION/event_1.md")

        # Ensure processed event description is created
        processed_event_path = "processed/EVENT_DESCRIPTION/event_1.md"
        processed_content = self.data_accessor.load_string(processed_event_path)
        assert "Hauptgericht" in processed_content

        # Ensure event description is stored in vector DB
        similar_docs = self.vector_db.find_similar_docs("Query Not Relevant for Mock")
        assert len(similar_docs) == 1
        assert similar_docs[0].page_content == processed_content

        # Ensure no generated messages are created yet
        self.__assert_no_files_in_folder("generated/message/TEAM")
        self.__assert_no_files_in_folder("generated/message/DINNER_ROUTE")

        # *** REQUEST 2: Process initial team message ***
        self.proposal_input_handler.process_request("input/message/TEAM/event_1.md")
        processed_team_message_path = "processed/message/TEAM/event_1.md"
        processed_team_content = self.data_accessor.load_string(processed_team_message_path)
        assert "Non Host Template" in processed_team_content
        assert "Message Template" in processed_team_content

        # *** REQUEST 3: Process initial dinner route message ***
        self.proposal_input_handler.process_request("input/message/DINNER_ROUTE/event_1.md")
        processed_dinner_route_path = "processed/message/DINNER_ROUTE/event_1.md"
        processed_dinner_content = self.data_accessor.load_string(processed_dinner_route_path)
        assert "Message Template" in processed_dinner_content
        assert "Self Template" in processed_dinner_content

        # Ensure no generated messages are created yet
        self.__assert_no_files_in_folder("generated/message/TEAM")
        self.__assert_no_files_in_folder("generated/message/DINNER_ROUTE")

        # Ensure no notifications were sent so far
        assert len(self.notification_handler.get_messages()) == 0

        # *** REQUEST 4: Process other event description to trigger message generation ***
        self.proposal_input_handler.process_request("input/EVENT_DESCRIPTION/event_2.md")

        # Ensure generated team message is created
        generated_team_path = "generated/message/TEAM/event_2.md"
        generated_team_content = self.data_accessor.load_string(generated_team_path)
        assert len(generated_team_content) > 0
        print ("*** Generated Team Message Content: ***")
        print (generated_team_content)
        assert "Heidelberg" in generated_team_content

        # Ensure generated dinner route message is created
        generated_dinner_route_path = "generated/message/DINNER_ROUTE/event_2.md"
        generated_dinner_content = self.data_accessor.load_string(generated_dinner_route_path)
        assert len(generated_dinner_content) > 0
        print ("*** Generated Dinner Route Message Content: ***")
        print (generated_dinner_content)
        assert "Heidelberg" in generated_dinner_content

        assert len(self.notification_handler.get_messages()) == 1
        notification_message = self.notification_handler.get_messages()[0]
        # assert notification message contains event description
        event2_description = self.data_accessor.load_string("input/EVENT_DESCRIPTION/event_2.md")
        assert event2_description in notification_message

    def __assert_no_files_in_folder(self, folder_path: str):
        files = os.listdir(self.source_bucket + "/" + folder_path)
        assert len(files) == 0, f"Expected no files in {folder_path}, but found: {files}"


