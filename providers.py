from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Dict, Any, Union, List
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    Ark = None

from models import ChatRequest, ChatResponse, StreamChunk, Message, Choice
from config import Config, ProviderConfig, load_config

class Provider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None
        self.async_client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        pass
    
    @abstractmethod
    def chat(self, request: ChatRequest) -> ChatResponse:
        pass
    
    @abstractmethod
    def chat_stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        pass
    
    @abstractmethod
    async def achat(self, request: ChatRequest) -> ChatResponse:
        pass
    
    @abstractmethod
    async def achat_stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        pass

class OpenAIProvider(Provider):
    def _set_default_model(self, request: ChatRequest):
        if not request.model:
            request.model = self.config.default_model
    
    def _initialize_client(self):
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        self.async_client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        self._set_default_model(request)
        response = self.client.chat.completions.create(**request.to_dict())
        return self._convert_response(response)
    
    def chat_stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        self._set_default_model(request)
        request.stream = True
        stream = self.client.chat.completions.create(**request.to_dict())
        for chunk in stream:
            yield self._convert_chunk(chunk)
    
    async def achat(self, request: ChatRequest) -> ChatResponse:
        self._set_default_model(request)
        response = await self.async_client.chat.completions.create(**request.to_dict())
        return self._convert_response(response)
    
    async def achat_stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        self._set_default_model(request)
        request.stream = True
        stream = await self.async_client.chat.completions.create(**request.to_dict())
        async for chunk in stream:
            yield self._convert_chunk(chunk)
    
    def _convert_response(self, response: ChatCompletion) -> ChatResponse:
        choices = []
        for choice in response.choices:
            content = choice.message.content
            message = Message.text(
                role=choice.message.role,
                content=content if content else ""
            )
            choices.append(Choice(
                index=choice.index,
                message=message,
                finish_reason=choice.finish_reason
            ))
        
        return ChatResponse(
            id=response.id,
            object=response.object,
            created=response.created,
            model=response.model,
            choices=choices,
            usage=response.usage.model_dump() if response.usage else None
        )
    
    def _convert_chunk(self, chunk: ChatCompletionChunk) -> StreamChunk:
        choices = []
        for choice in chunk.choices:
            delta = {}
            if choice.delta.content:
                delta["content"] = choice.delta.content
            if choice.delta.role:
                delta["role"] = choice.delta.role
            
            choices.append(Choice(
                index=choice.index,
                delta=delta,
                finish_reason=choice.finish_reason
            ))
        
        return StreamChunk(
            id=chunk.id,
            object=chunk.object,
            created=chunk.created,
            model=chunk.model,
            choices=choices
        )

class DeepSeekProvider(OpenAIProvider):
    pass

class QwenProvider(OpenAIProvider):
    pass

class DoubaoProvider(Provider):
    def _set_default_model(self, request: ChatRequest):
        if not request.model:
            request.model = self.config.default_model
    
    def _initialize_client(self):
        if not self.config.api_key:
            raise ValueError("Doubao API key is required")
        if Ark is None:
            raise ImportError("volcengine-python-sdk[ark] is required for DoubaoProvider")
        self.client = Ark(api_key=self.config.api_key)
        self.async_client = self.client
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        self._set_default_model(request)
        request_data = self._prepare_request(request)
        response = self.client.chat.completions.create(**request_data)
        return self._convert_response(response)
    
    def chat_stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        self._set_default_model(request)
        request_data = self._prepare_request(request)
        request_data['stream'] = True
        stream = self.client.chat.completions.create(**request_data)
        for chunk in stream:
            yield self._convert_chunk(chunk)
    
    async def achat(self, request: ChatRequest) -> ChatResponse:
        return self.chat(request)
    
    async def achat_stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        self._set_default_model(request)
        request_data = self._prepare_request(request)
        request_data['stream'] = True
        stream = self.client.chat.completions.create(**request_data)
        for chunk in stream:
            yield self._convert_chunk(chunk)
    
    def _prepare_request(self, request: ChatRequest) -> Dict[str, Any]:
        data = {
            "model": request.model,
            "messages": [self._convert_message(msg) for msg in request.messages]
        }
        
        if request.temperature is not None:
            data["temperature"] = request.temperature
        if request.max_tokens is not None:
            data["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            data["top_p"] = request.top_p
        if request.stop is not None:
            data["stop"] = request.stop
        if request.presence_penalty is not None:
            data["presence_penalty"] = request.presence_penalty
        if request.frequency_penalty is not None:
            data["frequency_penalty"] = request.frequency_penalty
        
        if self.config.thinking_enabled and not request.thinking:
            data["thinking"] = {"type": "enabled"}
        elif request.thinking:
            data["thinking"] = request.thinking
            
        return data
    
    def _convert_message(self, message: Message) -> Dict[str, Any]:
        if isinstance(message.content, str):
            return {"role": message.role.value, "content": message.content}
        else:
            content = []
            for item in message.content:
                if item.type.value == "text":
                    content.append({"type": "text", "text": item.text})
                elif item.type.value == "image_url":
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": item.image_url.url}
                    })
            return {"role": message.role.value, "content": content}
    
    def _convert_response(self, response) -> ChatResponse:
        choices = []
        for choice in response.choices:
            content = choice.message.content
            message = Message.text(
                role=choice.message.role,
                content=content if content else ""
            )
            choices.append(Choice(
                index=choice.index,
                message=message,
                finish_reason=choice.finish_reason
            ))
        
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return ChatResponse(
            id=response.id,
            object=response.object,
            created=response.created,
            model=response.model,
            choices=choices,
            usage=usage
        )
    
    def _convert_chunk(self, chunk) -> StreamChunk:
        choices = []
        for choice in chunk.choices:
            delta = {}
            if hasattr(choice.delta, 'content') and choice.delta.content:
                delta["content"] = choice.delta.content
            if hasattr(choice.delta, 'role') and choice.delta.role:
                delta["role"] = choice.delta.role
            
            choices.append(Choice(
                index=choice.index,
                delta=delta,
                finish_reason=choice.finish_reason
            ))
        
        return StreamChunk(
            id=chunk.id,
            object=chunk.object,
            created=chunk.created,
            model=chunk.model,
            choices=choices
        )

class ProviderHub:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.providers: Dict[str, Provider] = {}
        self._initialize_providers()
    
    def _apply_defaults(self, request: ChatRequest):
        if request.temperature is None:
            request.temperature = self.config.defaults.temperature
        if request.max_tokens is None:
            request.max_tokens = self.config.defaults.max_tokens
        if request.top_p is None:
            request.top_p = self.config.defaults.top_p
        if request.stream is None:
            request.stream = self.config.defaults.stream
    
    def _initialize_providers(self):
        provider_classes = {
            "openai": OpenAIProvider,
            "deepseek": DeepSeekProvider,
            "qwen": QwenProvider,
            "doubao": DoubaoProvider
        }
        
        for provider_name, provider_config in self.config.get_enabled_providers().items():
            if provider_name in provider_classes:
                try:
                    provider_class = provider_classes[provider_name]
                    self.providers[provider_name] = provider_class(provider_config)
                    print(f"Initialized provider: {provider_name}")
                except Exception as e:
                    print(f"Failed to initialize provider {provider_name}: {e}")
            else:
                print(f"Unknown provider: {provider_name}")
    
    def get_provider(self, provider_name: str) -> Optional[Provider]:
        return self.providers.get(provider_name)
    
    def list_providers(self) -> List[str]:
        return list(self.providers.keys())
    
    def list_models(self, provider_name: str) -> List[str]:
        provider = self.get_provider(provider_name)
        if provider:
            return provider.config.models
        return []
    
    def chat(self, provider_name: str, request: Union[ChatRequest, Dict[str, Any]]) -> ChatResponse:
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found or not enabled")
        
        if isinstance(request, dict):
            request = ChatRequest(**request)
        self._apply_defaults(request)
        
        return provider.chat_stream(request) if request.stream else provider.chat(request)
    
    async def achat(self, provider_name: str, request: Union[ChatRequest, Dict[str, Any]]) -> ChatResponse:
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found or not enabled")
        
        if isinstance(request, dict):
            request = ChatRequest(**request)
        self._apply_defaults(request)
        
        return provider.achat_stream(request) if request.stream else await provider.achat(request)
    
    def quick_chat(self, provider_name: str, prompt: str, model: Optional[str] = None) -> str:
        request = ChatRequest(
            messages=[Message.text(role="user", content=prompt)],
            model=model
        )
        response = self.chat(provider_name, request)
        return response.content or ""
    
    async def aquick_chat(self, provider_name: str, prompt: str, model: Optional[str] = None) -> str:
        request = ChatRequest(
            messages=[Message.text(role="user", content=prompt)],
            model=model
        )
        response = await self.achat(provider_name, request)
        return response.content or ""