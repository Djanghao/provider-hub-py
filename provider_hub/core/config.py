from dataclasses import dataclass
from typing import Optional, Dict, Any, Union, List

@dataclass
class LLMConfig:
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = 30
    max_retries: Optional[int] = 3
    thinking: Optional[Union[bool, str, Dict[str, Any]]] = None
    extra_headers: Optional[Dict[str, str]] = None
    extra_body: Optional[Dict[str, Any]] = None
    system_prompt: Optional[Union[str, List[Dict[str, Any]]]] = None
    stream: Optional[bool] = False
    stream_options: Optional[Dict[str, Any]] = None

@dataclass  
class ChatMessage:
    role: str
    content: Union[str, List[Dict[str, Any]]]

@dataclass
class ChatResponse:
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None