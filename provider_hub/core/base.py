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
        result = []
        sp = getattr(self.config, 'system_prompt', None)
        if sp:
            if isinstance(sp, str):
                result.append({"role": "system", "content": sp})
            elif isinstance(sp, list):
                for item in sp:
                    if isinstance(item, dict) and item["role"] == "system":
                        result.append(item)
                    else:
                        raise ValueError("system_prompt list items must be str or dict, and role must be 'system'")
    
        if isinstance(messages, str):
            result.append({"role": "user", "content": messages})
        else:
            for msg in messages:
                if isinstance(msg, ChatMessage):
                    if msg.role == "system":
                        raise ValueError("system_prompt should only be provided via initialization of a model")
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
        if self.config.stream is True:
            params["stream"] = self.config.stream
        if self.config.stream_options is not None:
            params["stream_options"] = self.config.stream_options
            
        params.update(kwargs)
        return params