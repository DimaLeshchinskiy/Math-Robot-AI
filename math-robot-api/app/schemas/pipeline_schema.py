from pydantic import BaseModel
from typing import Optional

class ProblemResult(BaseModel):
    """Individual problem result from pipeline"""
    problem_id: int
    filename: str
    latex_raw: Optional[str] = None
    latex_filtered: Optional[str] = None
    error: Optional[str] = None
    success: bool

class PipelineResponse(BaseModel):
    """Response model for complete pipeline processing"""
    total_problems: int
    successful: int
    failed: int
    results: list[ProblemResult]
    status: str
    processing_time: Optional[float] = None