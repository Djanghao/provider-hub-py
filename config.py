import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class ProviderConfig(BaseModel):
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: str
    default_model: str
    models: List[str] = Field(default_factory=list)
    timeout: int = 30
    max_retries: int = 3
    thinking_enabled: Optional[bool] = False

    class Config:
        extra = "allow"

class DefaultConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    top_p: float = 1.0

class Config(BaseModel):
    providers: Dict[str, ProviderConfig]
    defaults: DefaultConfig

    @classmethod
    def from_yaml(cls, config_path: str = "config.yaml") -> "Config":
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
        
        data = cls._replace_env_vars(data)
        
        providers = {}
        for provider_name, provider_data in data.get("providers", {}).items():
            providers[provider_name] = ProviderConfig(**provider_data)
        defaults = DefaultConfig(**data.get("defaults", {}))
        
        return cls(providers=providers, defaults=defaults)
    
    @staticmethod
    def _replace_env_vars(data: Any) -> Any:
        if isinstance(data, dict):
            return {k: Config._replace_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [Config._replace_env_vars(item) for item in data]
        elif isinstance(data, str):
            if data.startswith("${") and data.endswith("}"):
                env_var = data[2:-1]
                return os.getenv(env_var, data)
            return data
        else:
            return data

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        return self.providers.get(provider)
    
    def get_enabled_providers(self) -> Dict[str, ProviderConfig]:
        return {k: v for k, v in self.providers.items() if v.enabled}

def load_config(config_path: str = "config.yaml") -> Config:
    return Config.from_yaml(config_path)