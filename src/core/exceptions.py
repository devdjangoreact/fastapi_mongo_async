from fastapi import HTTPException, status


class TimeoutException(HTTPException):
    def __init__(self, detail: str = "Request timeout"):
        super().__init__(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=detail)


class RateLimitException(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ParsingException(HTTPException):
    def __init__(self, detail: str = "Parsing error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
