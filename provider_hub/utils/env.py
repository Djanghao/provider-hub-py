import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class EnvManager:
    ENV_KEY_MAPPING = {
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY", 
        "qwen": "DASHSCOPE_API_KEY",
        "doubao": "ARK_API_KEY"
    }
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        env_key = cls.ENV_KEY_MAPPING.get(provider.lower())
        if env_key:
            return os.getenv(env_key)
        return None
    
    @classmethod
    def get_provider_from_model(cls, model: str) -> str:
        if any(model.startswith(prefix) for prefix in ["gpt-", "gpt4", "gpt5"]):
            return "openai"
        elif model.startswith("deepseek"):
            return "deepseek"
        elif model.startswith("qwen"):
            return "qwen"
        elif model.startswith("doubao"):
            return "doubao"
        else:
            return "unknown"
    
    @classmethod
    def auto_detect_api_key(cls, model: str) -> Optional[str]:
        provider = cls.get_provider_from_model(model)
        return cls.get_api_key(provider)