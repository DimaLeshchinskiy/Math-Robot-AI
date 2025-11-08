from pydantic import BaseModel

class WhiteboardProcessingResponse(BaseModel):
    """Response model for whiteboard processing metadata"""
    problems_detected: int
    status: str
    message: str
    original_filename: str