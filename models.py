from typing import Optional, List, Union, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
import base64

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE_URL = "image_url"

class ImageDetail(str, Enum):
    LOW = "low"
    HIGH = "high"
    AUTO = "auto"

class ImageUrl(BaseModel):
    url: str
    detail: Optional[ImageDetail] = ImageDetail.AUTO

    @validator('url')
    def validate_url(cls, v):
        if v.startswith('data:image'):
            return v
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Image URL must start with http://, https://, or data:image')
        return v

class ContentItem(BaseModel):
    type: ContentType
    text: Optional[str] = None
    image_url: Optional[ImageUrl] = None

    @validator('text')
    def text_required_for_text_type(cls, v, values):
        if values.get('type') == ContentType.TEXT and not v:
            raise ValueError('text is required when type is "text"')
        return v

    @validator('image_url')
    def image_url_required_for_image_type(cls, v, values):
        if values.get('type') == ContentType.IMAGE_URL and not v:
            raise ValueError('image_url is required when type is "image_url"')
        return v

class Message(BaseModel):
    role: Role
    content: Union[str, List[ContentItem]]
    name: Optional[str] = None

    @classmethod
    def text(cls, role: Role, content: str) -> "Message":
        return cls(role=role, content=content)

    @classmethod
    def with_image(cls, role: Role, text: str, image_url: str, detail: ImageDetail = ImageDetail.AUTO) -> "Message":
        return cls(
            role=role,
            content=[
                ContentItem(type=ContentType.TEXT, text=text),
                ContentItem(
                    type=ContentType.IMAGE_URL,
                    image_url=ImageUrl(url=image_url, detail=detail)
                )
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self.content, str):
            return {"role": self.role.value, "content": self.content}
        else:
            content_list = []
            for item in self.content:
                if item.type == ContentType.TEXT:
                    content_list.append({"type": "text", "text": item.text})
                elif item.type == ContentType.IMAGE_URL:
                    content_list.append({
                        "type": "image_url",
                        "image_url": {
                            "url": item.image_url.url,
                            "detail": item.image_url.detail.value
                        }
                    })
            result = {"role": self.role.value, "content": content_list}
            if self.name:
                result["name"] = self.name
            return result

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, gt=0)
    stream: Optional[bool] = False
    top_p: Optional[float] = Field(None, ge=0, le=1)
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2)
    n: Optional[int] = Field(1, gt=0)
    thinking: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {"messages": [msg.to_dict() for msg in self.messages]}
        
        optional_fields = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
            "top_p": self.top_p,
            "stop": self.stop,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "thinking": self.thinking
        }
        
        for key, value in optional_fields.items():
            if value is not None:
                data[key] = value
        
        if self.n is not None and self.n != 1:
            data["n"] = self.n
            
        return data

class Choice(BaseModel):
    index: int
    message: Optional[Message] = None
    delta: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Dict[str, Any]] = None

    @property
    def content(self) -> Optional[str]:
        if self.choices and self.choices[0].message:
            content = self.choices[0].message.content
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                text_parts = [item.text for item in content if item.type == ContentType.TEXT]
                return "\n".join(text_parts) if text_parts else None
        return None

class StreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Choice]

    @property
    def content(self) -> Optional[str]:
        if self.choices and self.choices[0].delta:
            return self.choices[0].delta.get("content")
        return None

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_image}"