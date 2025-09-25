from typing import List, Union, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.base import BaseLLMProvider
from ..core.config import LLMConfig, ChatMessage, ChatResponse
from ..exceptions import APIKeyNotFoundError, ProviderConnectionError

try:
    from volcenginesdkarkruntime import Ark
    NATIVE_SDK_AVAILABLE = True
except ImportError:
    NATIVE_SDK_AVAILABLE = False
    from openai import OpenAI

class DoubaoProvider(BaseLLMProvider):
    SUPPORTED_MODELS = [
        "doubao-seed-1-6-250615",
        "doubao-seed-1-6-vision-250815", 
        "doubao-seed-1-6-flash-250828"
    ]
    
    OPENAI_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.api_key:
            raise APIKeyNotFoundError("Doubao API key is required")
        
        self.use_native_sdk = NATIVE_SDK_AVAILABLE and not config.base_url
        
        if self.use_native_sdk:
            self.client = Ark(
                api_key=config.api_key,
                timeout=config.timeout or 30
            )
        else:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url or self.OPENAI_BASE_URL,
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
            
            if self.use_native_sdk:
                return self._native_chat(formatted_messages, params)
            else:
                return self._openai_compatible_chat(formatted_messages, params)
                
        except Exception as e:
            raise ProviderConnectionError(f"Doubao API error: {str(e)}")

    def _native_chat(self, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> ChatResponse:
        thinking_params = self._prepare_thinking_params()
        return self._native_sync_chat(messages, params, thinking_params)

    def _openai_compatible_chat(self, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> ChatResponse:
        return self._sync_chat(messages, params)

    def _prepare_thinking_params(self) -> Dict[str, Any]:
        thinking_params = {}
        if self.config.thinking is not None:
            if isinstance(self.config.thinking, bool):
                thinking_params["thinking"] = {"type": "enabled" if self.config.thinking else "disabled"}
            elif isinstance(self.config.thinking, str):
                thinking_params["thinking"] = {"type": self.config.thinking}
            elif isinstance(self.config.thinking, dict):
                thinking_params["thinking"] = self.config.thinking
        return thinking_params

    def _native_sync_chat(self, messages: List[Dict[str, Any]], params: Dict[str, Any], thinking_params: Dict[str, Any]) -> ChatResponse:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            **params,
            **thinking_params
        )

        if params.get("stream") is True:
            return response
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )


    def _sync_chat(self, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> ChatResponse:
        extra_headers = self.config.extra_headers or {}
        if "x-is-encrypted" not in extra_headers:
            extra_headers["x-is-encrypted"] = "true"
            
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            extra_headers=extra_headers,
            **params
        )

        if params.get("stream") is True:
            return response
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )

