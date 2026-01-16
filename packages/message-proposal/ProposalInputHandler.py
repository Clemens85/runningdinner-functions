from DataAccessor import DataAccessor
from ProposalFileType import ProposalFileType
from Anonymizer import Anonymizer
from VectorDbRepository import VectorDbRepository
from DocumentVectorizable import DocumentVectorizable
from MessageProposalGenerator import MessageProposalGenerator
from llm.ChatOpenAI import ChatOpenAI
from InputRequest import InputRequest
from logger.Log import logger
from NotificationHandler import NotificationHandler

class ProposalInputHandler:
    def __init__(self, data_accessor: DataAccessor, vector_db_repository: VectorDbRepository, llm: ChatOpenAI, notification_handler: NotificationHandler = None):
        self.data_accessor = data_accessor
        self.vector_db_repository = vector_db_repository
        self.anonymizer = Anonymizer(llm=llm)
        self.data_accessor = data_accessor
        self.llm = llm
        self.notification_handler = notification_handler

    def process_request(self, storage_path: str):

        input_file_path = InputRequest(storage_path)
        proposal_file_type = input_file_path.get_proposal_file_type()
        
        logger.append_keys(admin_id=input_file_path.get_admin_id(), proposal_file_type=proposal_file_type.value)

        logger.info(f"Loading content from {storage_path} for proposal processing")
        content = self.data_accessor.load_string(storage_path)

        if proposal_file_type == ProposalFileType.EVENT_DESCRIPTION:
            self.__process_event_description(content, input_file_path)
        else:
            self.__process_message_text(content=content, proposal_file_type=proposal_file_type, input_file_path=input_file_path)

    def __process_event_description(self, content: str, input_file_path: InputRequest):
        
        logger.info(f"Processing event description for proposal generation")
        content_anonymized = self.anonymizer.anonymize_personal_data(content, ProposalFileType.EVENT_DESCRIPTION)
        processed_storage_path = input_file_path.get_processed_path()
        self.data_accessor.write_string_to_path(content_anonymized, processed_storage_path)

        # Workflow 1): Trigger message proposal generation
        # Very Important: Use original content (not anonymized) for proposal generation to ensure high quality proposals
        message_proposal_generator = MessageProposalGenerator(self.vector_db_repository, self.data_accessor, self.llm)
        resulting_proposals = message_proposal_generator.generate_proposals(content, input_file_path)

        # Workflow 2): Store event description in vector DB (for future proposal generations)
        admin_id = input_file_path.get_admin_id()
        doc_id = f"{ProposalFileType.EVENT_DESCRIPTION.value}_{admin_id}"
        document = DocumentVectorizable(
            page_content=content_anonymized,
            id=doc_id,
            admin_id=admin_id,
            type=ProposalFileType.EVENT_DESCRIPTION.value,
            source_path=processed_storage_path,
            metadata={}
        )
        self.vector_db_repository.add_document(document.id, document)

        if len(resulting_proposals) > 0 and self.notification_handler is not None:
            notification_message = self.notification_handler.build_notification_message(resulting_proposals)
            self.notification_handler.send_notification(notification_message)

    def __process_message_text(self, content: str, proposal_file_type: ProposalFileType, input_file_path: InputRequest):
        content_anonymized = self.anonymizer.anonymize_personal_data(content, proposal_file_type)
        self.data_accessor.write_string_to_path(content_anonymized, input_file_path.get_processed_path())