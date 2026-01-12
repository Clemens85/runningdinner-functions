import pytest
from InputRequest import InputRequest
from ProposalFileType import ProposalFileType


class TestGetProposalFileType:
    def test_event_description_uppercase(self):
        request = InputRequest("input/EVENT_DESCRIPTION/admin123.md")
        assert request.get_proposal_file_type() == ProposalFileType.EVENT_DESCRIPTION

    def test_event_description_lowercase(self):
        request = InputRequest("input/event_description/admin456.md")
        assert request.get_proposal_file_type() == ProposalFileType.EVENT_DESCRIPTION

    def test_participant_message_uppercase(self):
        request = InputRequest("input/message/PARTICIPANT_MESSAGE/admin789.md")
        assert request.get_proposal_file_type() == ProposalFileType.PARTICIPANT_MESSAGE

    def test_participant_message_lowercase(self):
        request = InputRequest("input/message/participant_message/admin101.md")
        assert request.get_proposal_file_type() == ProposalFileType.PARTICIPANT_MESSAGE

    def test_team_message_uppercase(self):
        request = InputRequest("input/message/TEAM_MESSAGE/admin202.md")
        assert request.get_proposal_file_type() == ProposalFileType.TEAM_MESSAGE

    def test_team_message_lowercase(self):
        request = InputRequest("input/message/team_message/admin303.md")
        assert request.get_proposal_file_type() == ProposalFileType.TEAM_MESSAGE

    def test_dinner_route_message_uppercase(self):
        request = InputRequest("input/message/DINNER_ROUTE_MESSAGE/admin404.md")
        assert request.get_proposal_file_type() == ProposalFileType.DINNER_ROUTE_MESSAGE

    def test_dinner_route_message_lowercase(self):
        request = InputRequest("input/message/dinner_route_message/admin505.md")
        assert request.get_proposal_file_type() == ProposalFileType.DINNER_ROUTE_MESSAGE

    def test_unknown_file_type_raises_error(self):
        request = InputRequest("input/message/unknown_type/admin606.md")
        with pytest.raises(ValueError, match="Unknown proposal file type"):
            request.get_proposal_file_type()


class TestGetProcessedPath:
    def test_replaces_input_with_processed(self):
        request = InputRequest("input/EVENT_DESCRIPTION/admin123.md")
        assert request.get_processed_path() == "processed/EVENT_DESCRIPTION/admin123.md"

    def test_handles_participant_message(self):
        request = InputRequest("input/message/PARTICIPANT_MESSAGE/admin456.md")
        assert request.get_processed_path() == "processed/message/PARTICIPANT_MESSAGE/admin456.md"

    def test_handles_team_message(self):
        request = InputRequest("input/message/TEAM_MESSAGE/admin789.md")
        assert request.get_processed_path() == "processed/message/TEAM_MESSAGE/admin789.md"

    def test_handles_dinner_route_message(self):
        request = InputRequest("input/message/DINNER_ROUTE_MESSAGE/admin101.md")
        assert request.get_processed_path() == "processed/message/DINNER_ROUTE_MESSAGE/admin101.md"


class TestGetAdminId:
    def test_extracts_admin_id_from_simple_path(self):
        request = InputRequest("input/EVENT_DESCRIPTION/admin123.md")
        assert request.get_admin_id() == "admin123"

    def test_extracts_admin_id_from_different_type(self):
        request = InputRequest("input/message/PARTICIPANT_MESSAGE/admin456.md")
        assert request.get_admin_id() == "admin456"

    def test_handles_different_file_extensions(self):
        request = InputRequest("input/EVENT_DESCRIPTION/admin789.txt")
        assert request.get_admin_id() == "admin789"

    def test_extracts_id_with_hyphens(self):
        request = InputRequest("input/EVENT_DESCRIPTION/admin-123-xyz.md")
        assert request.get_admin_id() == "admin-123-xyz"


class TestGetPathForGeneratedMessage:
    def test_generates_participant_message_path(self):
        request = InputRequest("input/event_description/admin123.md")
        path = request.get_path_for_generated_message(ProposalFileType.PARTICIPANT_MESSAGE)
        assert path == "generated/message/PARTICIPANT_MESSAGE/admin123.md"

    def test_generates_team_message_path(self):
        request = InputRequest("input/event_description/admin456.md")
        path = request.get_path_for_generated_message(ProposalFileType.TEAM_MESSAGE)
        assert path == "generated/message/TEAM_MESSAGE/admin456.md"

    def test_generates_team_message_path_from_other_message_path(self):
        request = InputRequest("input/message/DINNER_ROUTE_MESSAGE/admin456.md")
        path = request.get_path_for_generated_message(ProposalFileType.TEAM_MESSAGE)
        assert path == "generated/message/TEAM_MESSAGE/admin456.md"

    def test_generates_dinner_route_message_path(self):
        request = InputRequest("input/event_description/admin789.md")
        path = request.get_path_for_generated_message(ProposalFileType.DINNER_ROUTE_MESSAGE)
        assert path == "generated/message/DINNER_ROUTE_MESSAGE/admin789.md"

    def test_raises_error_for_event_description(self):
        request = InputRequest("input/event_description/admin101.md")
        with pytest.raises(ValueError, match="Cannot handle proposal file type"):
            request.get_path_for_generated_message(ProposalFileType.EVENT_DESCRIPTION)

    def test_raises_error_for_none_type(self):
        request = InputRequest("input/event_description/admin202.md")
        with pytest.raises(ValueError, match="Cannot handle proposal file type"):
            request.get_path_for_generated_message(None)


class TestBuildPathForProcessedMessageType:
    def test_builds_participant_message_path(self):
        request = InputRequest("input/event_description/admin123.md")
        path = request.build_path_for_processed_message_type("admin999", ProposalFileType.PARTICIPANT_MESSAGE)
        assert path == "processed/message/PARTICIPANT_MESSAGE/admin999.md"

    def test_builds_team_message_path(self):
        request = InputRequest("input/event_description/admin123.md")
        path = request.build_path_for_processed_message_type("admin888", ProposalFileType.TEAM_MESSAGE)
        assert path == "processed/message/TEAM_MESSAGE/admin888.md"

    def test_builds_dinner_route_message_path(self):
        request = InputRequest("input/EVENT_DESCRIPTION/admin123.md")
        path = request.build_path_for_processed_message_type("admin777", ProposalFileType.DINNER_ROUTE_MESSAGE)
        assert path == "processed/message/DINNER_ROUTE_MESSAGE/admin777.md"

    def test_raises_error_for_event_description(self):
        request = InputRequest("input/event_description/admin123.md")
        with pytest.raises(ValueError, match="Cannot handle proposal file type"):
            request.build_path_for_processed_message_type("admin666", ProposalFileType.EVENT_DESCRIPTION)

    def test_raises_error_for_none_type(self):
        request = InputRequest("input/event_description/admin123.md")
        with pytest.raises(ValueError, match="Cannot handle proposal file type"):
            request.build_path_for_processed_message_type("admin555", None)

    def test_raises_error_for_empty_admin_id(self):
        request = InputRequest("input/event_description/admin123.md")
        with pytest.raises(ValueError, match="Invalid admin id"):
            request.build_path_for_processed_message_type("", ProposalFileType.PARTICIPANT_MESSAGE)

    def test_raises_error_for_none_admin_id(self):
        request = InputRequest("input/event_description/admin123.md")
        with pytest.raises(ValueError, match="Invalid admin id"):
            request.build_path_for_processed_message_type(None, ProposalFileType.PARTICIPANT_MESSAGE)
