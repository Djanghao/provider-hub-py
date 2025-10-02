class ProviderHubError(Exception):
    pass

class ProviderNotSupportedError(ProviderHubError):
    pass

class ModelNotSupportedError(ProviderHubError):
    pass

class APIKeyNotFoundError(ProviderHubError):
    pass

class BaseUrlNotFoundError(ProviderHubError):
    pass

class ProviderConnectionError(ProviderHubError):
    pass

class RateLimitError(ProviderHubError):
    pass

class ThinkingNotSupportedError(ProviderHubError):
    pass