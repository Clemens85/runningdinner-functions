from openai import OpenAI
from ProposalFileType import ProposalFileType
from llm.ChatOpenAI import ChatOpenAI

ANONYMIZED_NAMES = ["Max Mustermann", "Maria Musterfrau", "John Doe", "Jane Smith", "Alex Johnson"]
ANONYMIZED_CITIES = ["Musterstadt", "Beispielhausen", "Sample City", "Exampletown", "Demoville"]
ANONYMIZED_STREETS = ["Musterstraße 1", "Beispielweg 2", "Sample Road 3", "Example Avenue 4", "Demo Boulevard 5"]
ANONYMIZED_EMAILS = ["max@mustermann.de", "maria@musterfrau.de", "john@doe.de", "jane@smith.de", "alex@johnson.de"]


def generate_anonymize_prompt(src_text: str, proposal_file_type: ProposalFileType) -> str:

    message_hint = ""
    if proposal_file_type != ProposalFileType.EVENT_DESCRIPTION:
        message_hint = """
        The given text is an Email message template markup file, which contains some placeholders like {firstname}, {firstname} {partner}, {host}, etc... which should not be changed or anonymized.
        There exist several sections in the text denoted by ## markup headers, like "## Subject", "## Message Template", "## Host Template" and so on.
        Ensure that these placeholders and markup headers are preserved exactly as they are in the anonymized text.
        """

    return f"""
    Anonymize the following text (which is very likely German, but can also be in English) by replacing personal data such as names (can be fullname or firstnames and lastnames), addresses, phone numbers and email addresses.
    Ensure that the anonymized text maintains the original meaning and context while removing all personal identifiers. You shall not change the text, just anonymize personal data.
    {message_hint}
    The given text is quite small, there will be only few personal data to anonymize. It is important to to not randomly invent new personal data, but use the following fixed anonymized data replacements:
    Names: {', '.join(ANONYMIZED_NAMES)}
    Cities: {', '.join(ANONYMIZED_CITIES)}
    Streets: {', '.join(ANONYMIZED_STREETS)}
    Emails: {', '.join(ANONYMIZED_EMAILS)}

    When you encounter one real name (like "Michael Becker"), replace it with the first of the anonymized names (like "Max Mustermann") and keep this replacement consistent throughout the text.
    If you encounter another next real name (like "Jona Schmidt") replace it with the next anonymized name in the list (like "Maria Musterfrau") and so on.
    This is very important to ensure that the same personal data is always replaced with the same anonymized data.
    
    There might be also other data to be anonymized like the following:
    - Zip postal codes (e.g 88535)
    - Mobile (phone) numbers (e.g. 0176 25345688)
    - Names of (public) locations / buildings (like cinemas, pubs, bars etc.)
    - Rivers (e.g. "Rhine", "Danube")
    For those data points, use invent suitable replacements that fit the context, but do not use any real personal data.
    
    Anonymize all these data points in a consistent manner, inventing suitable replacements that fit the context, but do not use any real personal data.

    Return only the anonymized text without any additional explanations.

    Here is the text to anonymize:\n\n{src_text}\n\nAnonymized text:
    """

class Anonymizer:

    def __init__(self, llm: ChatOpenAI, model: str = None, temperature: float = 0):
        self.llm = llm
        self.model = model
        self.temperature = temperature

    def anonymize_personal_data(self, text: str, proposal_file_type: ProposalFileType) -> str:
        anonymize_prompt = generate_anonymize_prompt(text, proposal_file_type)

        anonymization_response = self.llm.invoke(
            prompt=[
                {"role": "system", "content": "You are a helpful assistant that anonymizes personal data in texts."},
                {"role": "user", "content": anonymize_prompt}
            ],
            model_override=self.model,
            temperature_override=self.temperature
        )
        return anonymization_response.content