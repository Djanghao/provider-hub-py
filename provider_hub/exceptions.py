class ProviderHubError(Exception):
    pass

class ProviderNotSupportedError(ProviderHubError):
    pass

class ModelNotSupportedError(ProviderHubError):
    pass

class APIKeyNotFoundError(ProviderHubError):
    pass

class ProviderConnectionError(ProviderHubError):
    pass

class RateLimitError(ProviderHubError):
    pass

class ThinkingNotSupportedError(ProviderHubError):
    pass