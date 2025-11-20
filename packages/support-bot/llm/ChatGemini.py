import os
from typing import Optional, Type

from google import genai
from google.genai import types
from langchain_core.prompt_values import PromptValue
from pydantic import BaseModel

from llm.ChatModel import ChatModel
from llm.ChatResponse import ChatResponse


class ChatGemini(ChatModel):
    def __init__(self, model: str, temperature: float, api_key: Optional[str] = None):
        """
        Initialize ChatGemini with model configuration using the new Google Gen AI SDK.
        
        Args:
            model: Gemini model name (e.g., 'gemini-2.5-flash', 'gemini-2.5-pro')
            temperature: Temperature for response generation (0.0 to 2.0)
            api_key: Google AI API key (optional, reads from GOOGLE_API_KEY or GEMINI_API_KEY env var if not provided)
        """
        # Use provided API key or fall back to environment variables
        key = api_key or os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not key:
            raise ValueError("Google API key must be provided or set in GOOGLE_API_KEY/GEMINI_API_KEY environment variable")
        
        # Initialize the new unified Google Gen AI client
        self.client = genai.Client(api_key=key)
        self.model_name = model
        self.temperature = temperature

    def invoke(self, prompt: PromptValue, custom_response_class: Optional[Type[BaseModel]] = None) -> ChatResponse:
        """
        Invoke the Gemini model with the given prompt using the new SDK.
        
        Args:
            prompt: The prompt value containing messages
            custom_response_class: Optional Pydantic model for structured output
            
        Returns:
            ChatResponse containing the generated content
        """
        # Convert LangChain messages to simple text content
        # For now, concatenate all messages - you can enhance this later for multi-turn
        messages = prompt.to_messages()
        
        # Extract system instruction if present
        system_instruction = None
        user_messages = []
        
        for msg in messages:
            if msg.type == "system":
                system_instruction = msg.content
            else:
                # For user and assistant messages, add to conversation
                user_messages.append(msg.content)
        
        # Combine all user messages into a single prompt for simplicity
        # For multi-turn conversations, use client.chats.create() instead
        combined_content = "\n".join(user_messages) if user_messages else "Hello"
        
        # Build configuration
        config_params = {
            'temperature': self.temperature,
        }
        
        if system_instruction:
            config_params['system_instruction'] = system_instruction
        
        # Handle structured output with Pydantic models
        if custom_response_class is not None:
            config_params['response_mime_type'] = 'application/json'
            config_params['response_schema'] = custom_response_class
        
        config = types.GenerateContentConfig(**config_params)
        
        try:
            # Generate content using the new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=combined_content,
                config=config
            )
            
            answer = response.text
            return ChatResponse(
                content=answer,
                is_structured=custom_response_class is not None
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate content with Gemini: {str(e)}") from e

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"ChatGemini {self.model_name} with temperature {self.temperature}"
