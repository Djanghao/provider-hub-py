import base64
from typing import List, Union, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.base import BaseLLMProvider
from ..core.config import LLMConfig, ChatMessage, ChatResponse
from ..exceptions import APIKeyNotFoundError, ProviderConnectionError
from google import genai
from google.genai import types

class GeminiProvider(BaseLLMProvider):
    SUPPORTED_MODELS = [
        "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-2.0-flash-lite"
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.api_key:
            raise APIKeyNotFoundError("Gemini API key is required")
        self.client = genai.Client(api_key=config.api_key)

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
            prepared = self._prepare_messages(messages)
            contents = self._to_gemini_contents(prepared)
            gen_config = self._build_generation_config(**kwargs)

            stream = self.config.stream

            if stream:
                response = self.client.models.generate_content_stream(
                    model=self.config.model,
                    contents=contents,
                    config=types.GenerateContentConfig(**gen_config)
                )
                return response

            response = self.client.models.generate_content(
                model=self.config.model,
                contents=contents,
                config=types.GenerateContentConfig(**gen_config)
            )

            content_text = response.text
            usage = None
            usage_meta = response.usage_metadata
            if usage_meta:
                # Map Gemini usage to common fields
                prompt_tokens = getattr(usage_meta, "prompt_token_count", None)
                candidates_tokens = getattr(usage_meta, "candidates_token_count", None)
                total = None
                if prompt_tokens is not None and candidates_tokens is not None:
                    total = prompt_tokens + candidates_tokens
                usage = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": candidates_tokens,
                    "total_tokens": total
                }

            return ChatResponse(
                content=content_text,
                model=self.config.model,
                usage=usage,
                finish_reason=None
            )

        except Exception as e:
            raise ProviderConnectionError(f"Gemini API error: {str(e)}")

    def _build_generation_config(self, **kwargs) -> Dict[str, Any]:
        gen_config: Dict[str, Any] = {}
        if self.config.temperature is not None:
            gen_config["temperature"] = self.config.temperature
        if self.config.top_p is not None:
            gen_config["top_p"] = self.config.top_p
        if self.config.max_tokens is not None:
            gen_config["max_output_tokens"] = self.config.max_tokens
        if self.config.thinking is False and self.config.model.startswith("gemini-2.5"):
            gen_config["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        system_prompt = ""
        sp = getattr(self.config, 'system_prompt', None)
        if sp:
            if isinstance(sp, str):
                system_prompt += " " + sp
            elif isinstance(sp, list):
                for item in sp:
                    if isinstance(item, dict) and item["role"] == "system":
                        system_prompt += " " + item.get("content", "")
                    else:
                        raise ValueError("system_prompt list items must be str or dict, and role must be 'system'")
        if system_prompt.strip() != "":
            gen_config["system_instruction"] = system_prompt.strip()

        gen_config.update(kwargs)
        # Ignore other OpenAI-specific params silently
        return gen_config

    def _to_gemini_contents(self, messages: List[Dict[str, Any]]):
        # Build google.genai.types.Content objects (role + parts)
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                # handled separately as system_instruction
                continue
            if role == "assistant":
                role = "model"

            parts: List[types.Part] = []
            content = msg.get("content")
            if isinstance(content, str):
                parts.append(types.Part(text=content))
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(types.Part(text=item.get("text", "")))
                    elif isinstance(item, dict) and item.get("type") == "image_url":
                        url = (item.get("image_url") or {}).get("url")
                        if not url:
                            raise ProviderConnectionError("Gemini image_url missing 'url'")
                        if isinstance(url, str) and url.startswith("data:"):
                            try:
                                header, b64 = url.split(",", 1)
                                mime = header.split(":", 1)[1].split(";", 1)[0]
                                data = base64.b64decode(b64)
                                parts.append(types.Part(inline_data=types.Blob(mime_type=mime, data=data)))
                            except Exception:
                                raise ProviderConnectionError("Invalid data URL for image content")
                        else:
                            parts.append(types.Part.from_uri(url))
                    else:
                        raise ValueError("Gemini provider currently does not support the input content")
            elif content is not None:
                parts.append(types.Part(text=str(content)))

            contents.append(types.Content(role=role, parts=parts))
        return contents
