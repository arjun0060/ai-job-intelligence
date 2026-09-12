class AIServiceError(Exception):
    """Raised when AI service processing fails."""
    pass


class AIResponseParsingError(Exception):
    """Raised when AI response cannot be parsed."""
    pass