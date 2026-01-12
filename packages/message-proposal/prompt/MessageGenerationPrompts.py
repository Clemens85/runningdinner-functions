from typing import List
from ExampleMessage import ExampleMessage
from ProposalFileType import ProposalFileType

def get_message_generation_system_prompt() -> str:
  return """
You are an expert at drafting messages for running dinner events based on provided example messages and the descriptions of the events.
Given the event description and a set of example messages, your task is to generate a new messages that aligns with the style and tone of the examples while being tailored to the specific event description.
When generating the message, ensure that it is clear, engaging, and appropriate for the event context.
"""

def get_message_generation_user_prompt(input_event_description: str, examples: List[ExampleMessage], type: ProposalFileType) -> str:

    example_messages_str = "\n\n".join(
        [f"Example Message:\n{ex.message}\nEvent Description:\n{ex.event_description}" for ex in examples]
    )

    if type == ProposalFileType.PARTICIPANT_MESSAGE:
      return f"""
        Use the following example messages and their corresponding event description, to generate new participant messages for participants for a running dinner event.
        The example messages are written in markup format with sections like ## Subject and ## Message Template.
        The given message templates may contain placeholders like {{firstname}}, {{lastname}} which should also be used in the generated message template if reasonable.
        Here are the example messages and their event descriptions:\n\n{example_messages_str}\n\n
        Now, based on the above examples, generate a new participant message for the following event description :\n\n{input_event_description}\n\n
        Provide the message in the same markup format as the examples, including sections like ## Subject and ## Message Template.
      """
    elif type == ProposalFileType.TEAM_MESSAGE:
       return f"""
        Use the following example messages and their corresponding event description, to generate new team messages for teams for a running dinner event.
        The example messages are written in markup format with sections like ## Subject, ## Message Template, ## Host Template and ## Non Host Template.
        The ## Message Template may contain placeholders like {{firstname}}, {{lastname}}, {{partner}}, {{meal}}, {{mealspecifics}}, {{mealspecifics}}, {{host}}, {{managehostlink}} which should also be used in the generated message template if reasonable.
        The ## Non Host Template may contain placeholders like {{partner}} which should also be used in the generated non host template if reasonable.
        Here are the example messages and their event descriptions:\n\n{example_messages_str}\n\n
        Now, based on the above examples, generate a new team message for the following event description :\n\n{input_event_description}\n\n
        Provide the message in the same markup format as the examples, including sections like ## Subject, ## Message Template, ## Host Template and ## Non Host Template.
    """
    elif type == ProposalFileType.DINNER_ROUTE_MESSAGE:
       return f"""
        Use the following example messages and their corresponding event description, to generate new dinner route messages for teams for a running dinner event.
        The example messages are written in markup format with sections like ## Subject, ## Message Template, ## Hosts Template and ## Self Template.
        The ## Message Template may contain placeholders like {{firstname}}, {{lastname}}, {{route}} {{routelink}} which should also be used in the generated message template if reasonable.
        The ## Hosts Template may contain placeholders like  {{firstname}}, {{lastname}}, {{meal}}, {{mealtime}}, {{mealspecifics}} which should also be used in the generated hosts template if reasonable.
        The ## Self Template may contain placeholders like  {{firstname}}, {{lastname}}, {{meal}}, {{mealtime}}, {{hostaddress}}, {{mobilenumber}} which should also be used in the generated self template if reasonable.
        Here are the example messages and their event descriptions:\n\n{example_messages_str}\n\n
        Now, based on the above examples, generate a new dinner route message for the following event description :\n\n{input_event_description}\n\n
        Provide the message in the same markup format as the examples, including sections like ## Subject, ## Message Template, ## Hosts Template and ## Self Template.
    """

    raise ValueError(f"Unsupported ProposalFileType for message generation: {type}")