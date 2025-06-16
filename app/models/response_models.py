from pydantic import BaseModel

class SuccessResponse(BaseModel):
    status: str
    message: str

class ErrorResponse(BaseModel):
    status: str
    message: str
