from typing import List
from DataAccessor import DataAccessor
from TextTranslation import TextTranslation
from Translator import Translator, is_not_german
from VectorDbRepository import VectorDbRepository
from InputRequest import InputRequest
from ProposalFileType import ProposalFileType
from DocumentVectorizable import DocumentVectorizable
from llm.ChatOpenAI import ChatOpenAI
from logger.Log import logger
from prompt.MessageGenerationPrompts import get_message_generation_system_prompt, get_message_generation_user_prompt
from ExampleMessage import ExampleMessage

MAX_SIMILAR_DOCS = 12
MAX_EXAMPLES_PER_TYPE = 3
PROPOSAL_TYPES = [ProposalFileType.TEAM, ProposalFileType.DINNER_ROUTE, ProposalFileType.PARTICIPANT]

class MessageProposalGenerator:
    def __init__(self, vector_db_repository: VectorDbRepository, data_accessor: DataAccessor, llm: ChatOpenAI):
        self.vector_db_repository = vector_db_repository
        self.data_accessor = data_accessor
        self.llm = llm
        self.examples: List[ExampleMessage] = []
        self.generation_results: List[ExampleMessage] = []
        self.translator = Translator(self.llm)

    def generate_proposals(self, event_description: TextTranslation, request: InputRequest) -> List[ExampleMessage]:
        logger.info(f"Generating message proposals for event description")
        current_admin_id = request.get_admin_id()
        similar_event_desc_docs = self.vector_db_repository.find_similar_docs(event_description.german_translation, top_k=MAX_SIMILAR_DOCS, exclude_admin_id=current_admin_id)
        if not similar_event_desc_docs or len(similar_event_desc_docs) == 0:
            logger.warning(f"No similar event descriptions found in vector database for event description")
            return []  # No similar documents found, cannot generate proposals

        logger.info(f"Found {len(similar_event_desc_docs)} similar event descriptions in vector database for event description")
        for similar_event_desc_doc in similar_event_desc_docs:
            if all(self.__examples_count_for_type(t) >= MAX_EXAMPLES_PER_TYPE for t in PROPOSAL_TYPES):
                logger.info(f"All message types have reached {MAX_EXAMPLES_PER_TYPE} examples, stopping early")
                break
            for proposal_type in PROPOSAL_TYPES:
                if self.__examples_count_for_type(proposal_type) < MAX_EXAMPLES_PER_TYPE:
                    self.__add_message_of_event_to_examples(similar_event_desc_doc, request, proposal_type)

        self.__generate_message_proposal(event_description=event_description, proposal_type=ProposalFileType.TEAM, request=request)
        self.__generate_message_proposal(event_description=event_description, proposal_type=ProposalFileType.DINNER_ROUTE, request=request)
        self.__generate_message_proposal(event_description=event_description, proposal_type=ProposalFileType.PARTICIPANT, request=request)

        return self.generation_results

    def __examples_count_for_type(self, proposal_type: ProposalFileType) -> int:
        return sum(1 for ex in self.examples if ex.type == proposal_type)

    def __add_message_of_event_to_examples(self, event_desc_doc: DocumentVectorizable, request: InputRequest, proposal_type: ProposalFileType):
        message_content = self.__get_message_content(event_desc_doc, request, proposal_type)
        if message_content:
            self.examples.append(ExampleMessage(message=message_content, event_description=event_desc_doc.page_content, type=proposal_type))

    def __get_message_content(self, event_description_document: DocumentVectorizable, request: InputRequest, proposal_file_type: ProposalFileType) -> str | None:
        admin_id = event_description_document.admin_id
        message_storage_path = request.build_path_for_processed_message_type(admin_id, proposal_file_type)
        logger.info(f"Loading message content from {message_storage_path} for proposal generation")
        try:
            return self.data_accessor.load_string(message_storage_path)
        except Exception as e:
            logger.exception(f"Failed to load message content from {message_storage_path}. This maybe also be due to file does not exist: {str(e)}")
            return None

    def __generate_message_proposal(self, event_description: TextTranslation, proposal_type: ProposalFileType, request: InputRequest):

        examples_for_type = [ex for ex in self.examples if ex.type == proposal_type]
        if len(examples_for_type) == 0:
            logger.warning(f"No example messages available to generate proposal for type {proposal_type}")
            return
        
        logger.info(f"Generating message proposal for type {proposal_type} using {len(examples_for_type)} example messages")

        generation_prompt = get_message_generation_user_prompt(input_event_description=event_description.german_translation,
                                                               examples=examples_for_type,
                                                               proposal_type=proposal_type)
        result = self.llm.invoke(
            prompt=[
                {
                    "role": "system",
                    "content": get_message_generation_system_prompt()
                },
                {
                    "role": "user",
                    "content": generation_prompt
                }
            ]
        )
        proposal_text = result.content

        if is_not_german(event_description.original_language):
            proposal_text = self.translator.translate_to_language(proposal_text, event_description.original_language)

        proposal_storage_path = request.get_path_for_generated_message(proposal_type)
        logger.info(f"Storing generated message proposal for type {proposal_type} at {proposal_storage_path}")
        self.data_accessor.write_string_to_path(proposal_text, proposal_storage_path)

        self.generation_results.append(ExampleMessage(message=proposal_text, event_description=event_description.original, type=proposal_type))
