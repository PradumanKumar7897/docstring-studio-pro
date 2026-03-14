class AIProviderError(Exception):
    pass


class AIQuotaError(AIProviderError):
    pass


class AITimeoutError(AIProviderError):
    pass