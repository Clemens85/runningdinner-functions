from ProposalFileType import ProposalFileType

class InputRequest:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def get_proposal_file_type(self) -> ProposalFileType:
        storage_path = self.storage_path
        if "EVENT_DESCRIPTION" in storage_path.upper():
            return ProposalFileType.EVENT_DESCRIPTION
        elif "PARTICIPANT" in storage_path.upper():
            return ProposalFileType.PARTICIPANT_MESSAGE
        elif "TEAM" in storage_path.upper():
            return ProposalFileType.TEAM_MESSAGE
        elif "DINNER_ROUTE" in storage_path.upper():
            return ProposalFileType.DINNER_ROUTE_MESSAGE
        raise ValueError(f"Unknown proposal file type for storage path: {storage_path}")

    def get_processed_path(self) -> str:
        """
        Maps the wrapped storage path to the processed storage path.
        Example: input/event_descriptions/admin123.md -> processed/event_descriptions/admin123.md
        """

        storage_path = self.storage_path
        parts = storage_path.split('/')
        parts[0] = "processed"
        return '/'.join(parts)

    def get_admin_id(self) -> str:
        """
        Extracts the admin ID from the storage path.
        Example: input/event_descriptions/admin123.md -> admin123
        """
        storage_path = self.storage_path
        filename = storage_path.split('/')[-1]
        admin_id = filename.split('.')[0]
        return admin_id

    def get_path_for_generated_message(self, proposal_file_type: ProposalFileType) -> str:
        """
        Builds the storage path for a given message type and the admin-id of this request for a generated message (proposal).
        Example: admin123, PARTICIPANT_MESSAGE -> generated/PARTICIPANT_MESSAGE/admin123.md
        """
        if proposal_file_type is None or proposal_file_type == ProposalFileType.EVENT_DESCRIPTION:
            raise ValueError(f"Cannot handle proposal file type: {proposal_file_type}")
        
        admin_id = self.get_admin_id()
        if admin_id is None or admin_id == "":
            raise ValueError(f"Cannot extract admin id from storage path: {self.storage_path}")
        
        base_path = "generated/message"
        return f"{base_path}/{proposal_file_type.value}/{admin_id}.md"
    
    def build_path_for_processed_message_type(self, admin_id: str, proposal_file_type: ProposalFileType) -> str:
        """
        Builds the storage path for a given message type and admin id.
        Example: admin123, PARTICIPANT_MESSAGE -> input/PARTICIPANT_MESSAGE/admin123.md
        """
        if proposal_file_type is None or proposal_file_type == ProposalFileType.EVENT_DESCRIPTION:
            raise ValueError(f"Cannot handle proposal file type: {proposal_file_type}")
        
        if admin_id is None or admin_id == "":
            raise ValueError(f"Invalid admin id: {admin_id}")
        
        base_path = "processed/message"
        return f"{base_path}/{proposal_file_type.value}/{admin_id}.md"

