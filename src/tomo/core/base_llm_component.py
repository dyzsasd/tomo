import logging
import os
import time
from typing import Optional, Dict, Any, List

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.llms import LlamaCpp, HuggingFaceHub


logger = logging.getLogger(__name__)


class BaseLLMComponent:
    """Base class for LLM-based components with common initialization and utilities"""

    llm_map = {
        "openai": ChatOpenAI,
        "azure_openai": AzureChatOpenAI,
        "llamacpp": LlamaCpp,
        "huggingfacehub": HuggingFaceHub,
    }

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.llm_config = llm_config or {}
        self.llm = self._initialize_llm()
        self.prompt = None

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration"""
        llm_type = self.llm_config.get("llm_type", "openai")
        llm_params = self.llm_config.get("llm_params", {})

        if llm_type not in self.llm_map:
            raise ValueError(f"LLM type '{llm_type}' is not supported.")

        return self.llm_map[llm_type](**llm_params)

    def _setup_chain(self, system_prompt: str, human_prompt: str, output_parser):
        """Set up the LLM processing chain"""
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(human_prompt),
            ]
        )
        return self.prompt | self.llm | output_parser

    def _save_prompts(self, session_id: str, prompts: List[str], prefix: str):
        """Save prompts to files for debugging"""
        directory_path = os.path.join("session_logs", str(session_id))
        os.makedirs(directory_path, exist_ok=True)

        timestamp = round(time.time())
        for idx, content in enumerate(prompts):
            prompt_type = "system" if idx == 0 else "user"
            filename = f"session_logs/{session_id}/{timestamp}-{prefix}_{prompt_type}_prompt.txt"
            with open(filename, "w") as fh:
                fh.write(content)
