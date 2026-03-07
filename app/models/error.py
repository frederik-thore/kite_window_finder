from pydantic import BaseModel


class ApiError(BaseModel):
    code: str
    message: str
    details: list[str] | None = None


class ErrorEnvelope(BaseModel):
    error: ApiError
