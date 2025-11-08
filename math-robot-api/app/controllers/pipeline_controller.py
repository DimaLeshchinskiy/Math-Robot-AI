from fastapi import Depends, APIRouter, UploadFile, File, HTTPException, status
import time

from app.services.auth_service import basic_auth
from app.services.file_service import FileService
from app.services.pipeline_service import PipelineService
from app.schemas.pipeline_schema import PipelineResponse, ProblemResult

router = APIRouter()

@router.post(
    "/pipeline/{target_regions}",
    response_model=PipelineResponse,
    summary="Complete Pipeline",
    description="""
    Complete processing pipeline for whiteboard images:
    
    1. **Detection**: Identify and extract individual mathematical problems
    2. **OCR Conversion**: Convert each problem to LaTeX using machine learning
    3. **Structured Output**: Return organized results ready for further processing
    
    This endpoint handles the entire workflow from raw image to processed LaTeX formulas.
    """,
    response_description="Structured results of pipeline processing",
    responses={
        200: {"description": "Successfully processed whiteboard and generated LaTeX"},
        401: {"description": "Unauthorized - Invalid credentials"},
        400: {"description": "Bad Request - Invalid file type or no problems detected"},
        415: {"description": "Unsupported Media Type - File must be an image"},
        500: {"description": "Internal Server Error - Failed to process pipeline"},
    }
)
async def process_pipeline(
    target_regions: int,
    file: UploadFile = File(..., description="Whiteboard image containing mathematical problems"),
    username: str = Depends(basic_auth)
) -> PipelineResponse:
    """
    Complete pipeline processing for whiteboard images.

    - **target_regions**: Number of expressions expected in the image (1-20, required)
    - **file**: Whiteboard image with multiple math problems (required)
    - **Returns**: Structured results with LaTeX formulas and processing status

    **Pipeline Steps**:
    1. Problem detection and segmentation
    2. LaTeX conversion for each problem
    3. Quality assessment and error handling

    **Next Steps**: Results can be sent to Wolfram Alpha for solving
    """
    start_time = time.time()
    
    try:
        if target_regions > 20 or target_regions < 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="target_regions should be betwwen 1 and 20")
        
        # Validate and convert to internal file model
        internal_file = await FileService.validate_and_convert(file)
        
        # Process through pipeline
        raw_results = await PipelineService.process_pipeline(internal_file, target_regions=target_regions)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Convert to structured response
        successful = sum(1 for r in raw_results if r.get('success', False))
        failed = len(raw_results) - successful
        
        # Convert raw results to ProblemResult objects
        problem_results = []
        for result in raw_results:
            problem_results.append(ProblemResult(
                problem_id=result.get('problem_id', 0),
                filename=result.get('filename', ''),
                latex_raw=result.get('latex_raw', ''),
                latex_filtered=result.get('latex_filtered', ''),
                error=result.get('error'),
                success=result.get('success', False)
            ))
        
        return PipelineResponse(
            total_problems=len(raw_results),
            successful=successful,
            failed=failed,
            results=problem_results,
            status="success",
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline processing failed: {str(e)}"
        )