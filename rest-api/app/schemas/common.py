from pydantic import BaseModel

class DeleteResponse(BaseModel):
    """Schema for delete operation response"""
    success: bool
    message: str