import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

class Configuration(BaseModel):
    """The configuration for the agent."""

    answer_model: str = Field(
        default="gpt-4o-mini",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    temperature: float = Field(
        default=0.2,
        metadata={"description": "The temperature to use for the language models."},
    )

    max_similar_docs: int = Field(
        default=1,
        metadata={"description": "The maximum number of similar documents to retrieve."},
    )

    runningdinner_api_host: str = Field(
        default="https://localhost:3000",
        metadata={"description": "The host of the RunningDinner API."},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)