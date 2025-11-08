from pydantic import BaseModel

class LatexResponse(BaseModel):
    """Response model for LaTeX extraction"""
    latex: str
    status: str = "success"
    message: str = "LaTeX formula extracted successfully"