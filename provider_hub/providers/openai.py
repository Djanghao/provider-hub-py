from typing import List, Union, Dict, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.base import BaseLLMProvider
from ..core.config import LLMConfig, ChatMessage, ChatResponse
from ..exceptions import APIKeyNotFoundError, ProviderConnectionError

class OpenAIProvider(BaseLLMProvider):
    SUPPORTED_MODELS = [
        "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1"
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.api_key:
            raise APIKeyNotFoundError("OpenAI API key is required")
        
        self.client = OpenAI(
            api_key=config.api_key,
            timeout=config.timeout
        )

    def get_supported_models(self) -> List[str]:
        return self.SUPPORTED_MODELS

    def validate_config(self) -> bool:
        return self.config.api_key is not None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def chat(self, messages: Union[str, List[ChatMessage]], **kwargs) -> ChatResponse:
        try:
            formatted_messages = self._prepare_messages(messages)
            params = self._merge_config(**kwargs)
            return self._sync_chat(formatted_messages, params)
                
        except Exception as e:
            raise ProviderConnectionError(f"OpenAI API error: {str(e)}")

    def _sync_chat(self, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> ChatResponse:
        if self.config.model.startswith('gpt-5'):
            if 'max_tokens' in params:
                params['max_completion_tokens'] = params.pop('max_tokens')
            if 'temperature' in params and params['temperature'] != 1:
                params.pop('temperature')
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            **params
        )
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )

