from fastapi import Depends, APIRouter, UploadFile, File, Response, HTTPException
from typing import Optional
import zipfile
import io
from app.services.auth_service import basic_auth
from app.services.file_service import FileService
from app.services.whiteboard_processor_service import WhiteboardProcessorService

router = APIRouter()

@router.post(
    "/whiteboard/problems",
    summary="Extract Mathematical Problems from Whiteboard",
    responses={
        200: {"description": "Successfully extracted mathematical problems"},
        401: {"description": "Unauthorized - Invalid credentials"},
        400: {"description": "Bad Request - Invalid file type or no problems detected"},
        415: {"description": "Unsupported Media Type - File must be an image"},
        500: {"description": "Internal Server Error - Failed to process image"},
    }
)
async def extract_whiteboard_problems(
    file: UploadFile = File(..., description="Whiteboard image containing mathematical problems"),
    username: str = Depends(basic_auth)
) -> Response:
    """Extract individual mathematical problems from a whiteboard image"""
    try:

        internal_file = await FileService.validate_and_convert(file)
        problem_files = await WhiteboardProcessorService.extract_problems(internal_file)
        
        # Create ZIP response
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, problem_file in enumerate(problem_files):
                image_bytes = await problem_file.to_bytes()
                zip_file.writestr(f"problem_{i+1:02d}.png", image_bytes)
        
        zip_buffer.seek(0)
        
        # Create filename
        original_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
        zip_filename = f"{original_name}_extracted_problems.zip"
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}",
                "X-Problems-Detected": str(len(problem_files))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process whiteboard: {str(e)}"
        )