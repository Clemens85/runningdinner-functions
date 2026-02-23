from typing import List
from ExampleMessage import ExampleMessage
from ProposalFileType import ProposalFileType

def get_message_generation_system_prompt() -> str:
  return """
You are an expert at drafting messages for running dinner events based on provided example messages and their corresponding descriptions of events.
Given the input event description and a set of example messages / example description pairs, your task is to generate a new message that align with the style and tone of the examples while being tailored to the specific input event description.
Important: Detect the language of the input event description and write the entire output in that same language. 
When generating a new message, ensure that it is clear, engaging, and appropriate for the event context.
When generating a new message, only use factual information that is explicitly provided in the input event description. Do not use factual details from the example messages, as those are from other events and not applicable. Do not invent or assume event details such as dates, times, locations, organizer names, or event rules that are not present in the input event description. 
"""

def generate_sections_advice(sections_template: str) -> str:
    return f"""
    Provide the message in the same Markdown as the examples, including sections like {sections_template}.
    Important: Don't introduce new sections, just use the mentioned sections: {sections_template}.
    """

def get_message_generation_user_prompt(input_event_description: str, examples: List[ExampleMessage], proposal_type: ProposalFileType) -> str:

    example_messages_str = "\n\n".join(
        [f"Example Message:\n{ex.message}\nCorresponding Event Description:\n{ex.event_description}" for ex in examples]
    )

    message_placeholders = "{firstname}, {lastname}"
    if proposal_type == ProposalFileType.TEAM:
        message_placeholders += ", {partner}, {meal}, {mealtime}, {mealspecifics}, {host}, {managehostlink}"
    elif proposal_type == ProposalFileType.DINNER_ROUTE:
        message_placeholders += ", {route}, {routelink}"

    placeholder_instruction = f"""
    The provided placeholders (e.g. {message_placeholders}, etc.) represent dynamic data that will be filled in by our email system at send time.
    When generating the message template:
    - Use the listed placeholders wherever the context calls for personalized or dynamic data (e.g. use {{firstname}} instead of writing a concrete name).
    - Never substitute a placeholder with concrete/hardcoded data (exception: you may use data from the event description like contact persons or after party locations).
    - You may omit placeholders that are not relevant to the generated message, but do not invent new placeholder names that are not in the provided list.
    """


    participant_sections = "## Subject and ## Message Template"
    team_sections = "## Subject, ## Message Template, ## Host Template and ## Non Host Template"
    dinner_route_sections = "## Subject, ## Message Template, ## Hosts Template and ## Self Template"

    if proposal_type == ProposalFileType.PARTICIPANT:
      return f"""
        Use the following example messages and their corresponding event description, to generate a new participant message for participants for a running dinner event.
        The example messages are written in Markdown with sections like {participant_sections}.
        The given message templates may contain placeholders like {{firstname}}, {{lastname}} which should also be used in the generated message template if reasonable.
        
        {generate_sections_advice(participant_sections)}        
        {placeholder_instruction}
        
        Here are the example messages and their event descriptions:\n\n{example_messages_str}\n\n
        Now, based on the above examples, generate a new participant message for the following input event description :\n\n{input_event_description}\n\n
      """
    elif proposal_type == ProposalFileType.TEAM:
       return f"""
        Use the following example messages and their corresponding event description, to generate a new team message for teams for a running dinner event.
        The example messages are written in Markdown with sections like {team_sections}.
        The ## Message Template may contain placeholders like {{firstname}}, {{lastname}}, {{partner}}, {{meal}}, {{mealtime}}, {{mealspecifics}}, {{host}}, {{managehostlink}} which should also be used in the generated message template if reasonable.
        The ## Non Host Template may contain placeholders like {{partner}} which should also be used in the generated non host template if reasonable.
        
        {generate_sections_advice(team_sections)}
        {placeholder_instruction}
        
        Here are the example messages and their event descriptions:\n\n{example_messages_str}\n\n
        Now, based on the above examples, generate a new team message for the following input event description :\n\n{input_event_description}\n\n
    """
    elif proposal_type == ProposalFileType.DINNER_ROUTE:
       return f"""
        Use the following example messages and their corresponding event description, to generate a new dinner route message for teams for a running dinner event.
        The example messages are written in Markdown with sections like {dinner_route_sections}.
        The ## Message Template may contain placeholders like {{firstname}}, {{lastname}}, {{route}}, {{routelink}} which should also be used in the generated message template if reasonable.
        The ## Hosts Template may contain placeholders like {{firstname}}, {{lastname}}, {{meal}}, {{mealtime}}, {{mealspecifics}} which should also be used in the generated hosts template if reasonable.
        The ## Self Template may contain placeholders like {{firstname}}, {{lastname}}, {{meal}}, {{mealtime}}, {{hostaddress}}, {{mobilenumber}} which should also be used in the generated self template if reasonable.
        
        {generate_sections_advice(dinner_route_sections)}
        {placeholder_instruction}
        
        Here are the example messages and their event descriptions:\n\n{example_messages_str}\n\n
        Now, based on the above examples, generate a new dinner route message for the following input event description :\n\n{input_event_description}\n\n
    """

    raise ValueError(f"Unsupported ProposalFileType for message generation: {proposal_type}")