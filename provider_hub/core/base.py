from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, List
from .config import LLMConfig, ChatMessage, ChatResponse

class BaseLLMProvider(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def chat(self, messages: Union[str, List[ChatMessage]], **kwargs) -> ChatResponse:
        pass

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        pass

    def _prepare_messages(self, messages: Union[str, List[ChatMessage]]) -> List[Dict[str, Any]]:
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        
        result = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                result.append({"role": msg.role, "content": msg.content})
            else:
                result.append(msg)
        return result

    def _merge_config(self, **kwargs) -> Dict[str, Any]:
        params = {}
        
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature
        if self.config.top_p is not None:
            params["top_p"] = self.config.top_p
        if self.config.max_tokens is not None:
            params["max_tokens"] = self.config.max_tokens
            
        params.update(kwargs)
        return params