from fastapi import Depends, APIRouter, UploadFile, File, HTTPException
from app.services.auth_service import basic_auth
from app.services.file_service import FileService
from app.services.pix2text_service import Pix2TextService
from app.schemas.latex_schema import LatexResponse

router = APIRouter()

@router.post(
    "/latext",
    response_model=LatexResponse,
    summary="Extract LaTeX from Image",
    responses={
        200: {"description": "Successfully extracted LaTeX formula"},
        401: {"description": "Unauthorized - Invalid credentials"},
        400: {"description": "Bad Request - Invalid file type or no formula detected"},
        415: {"description": "Unsupported Media Type - File must be an image"},
        500: {"description": "Internal Server Error - Failed to process image"},
    }
)
async def get_latext_from_image(
    file: UploadFile = File(..., description="Image containing mathematical formula"),
    username: str = Depends(basic_auth)
) -> LatexResponse:
    """Extract LaTeX formula from an uploaded image"""
    try:
        internal_file = await FileService.validate_and_convert(file)
        latex_result = await Pix2TextService.recognize_formula(internal_file)
        
        if not latex_result or latex_result.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="No formula detected in the image"
            )
        
        return LatexResponse(
            latex=latex_result,
            status="success",
            message="LaTeX formula extracted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract LaTeX: {str(e)}"
        )