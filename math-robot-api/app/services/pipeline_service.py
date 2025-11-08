import asyncio
import logging
from typing import List, Dict, Any
from fastapi import HTTPException

from app.models.file_model import File
from app.services.whiteboard_processor_service import WhiteboardProcessorService
from app.services.pix2text_service import Pix2TextService
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

class PipelineService:
    """
    Simplified pipeline service that orchestrates the entire workflow.
    Uses static methods and internal File model.
    """
    
    @staticmethod
    async def process_pipeline(file: File, padding_ratio: float = 0.05) -> List[Dict[str, Any]]:
        """
        Complete pipeline: split whiteboard → OCR each problem → return LaTeX results
        
        Args:
            file: Internal File model
            padding_ratio: Padding for problem detection
            
        Returns:
            List of dictionaries containing problem data and LaTeX results
        """
        try:
            # Step 1: Split whiteboard into individual problems
            logger.info("Step 1: Splitting whiteboard image into individual problems")
            problem_files = await WhiteboardProcessorService.extract_problems(file, padding_ratio)
            
            if not problem_files:
                raise HTTPException(status_code=400, detail="No mathematical problems detected in the image")
            
            logger.info(f"Step 1 complete: Found {len(problem_files)} problems")
            
            # Step 2: Process each problem with Pix2Text to get LaTeX
            logger.info("Step 2: Converting problems to LaTeX using OCR")
            results = await PipelineService._process_problems_with_ocr(problem_files)
            
            logger.info(f"Step 2 complete: Successfully processed {len(results)} problems")
            
            return results
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")
    
    @staticmethod
    async def _process_problems_with_ocr(problem_files: List[File]) -> List[Dict[str, Any]]:
        """
        Process each problem file with Pix2Text to generate LaTeX
        """
        # Process all problems concurrently
        tasks = []
        for i, problem_file in enumerate(problem_files):
            task = PipelineService._process_single_problem(problem_file, i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process problem {i+1}: {str(result)}")
                processed_results.append({
                    "problem_id": i + 1,
                    "filename": problem_files[i].name,
                    "latex_raw": None,
                    "latex_filtered": None,
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    @staticmethod
    async def _process_single_problem(problem_file: File, index: int) -> Dict[str, Any]:
        """
        Process a single problem file: OCR → LaTeX → Filter via Ollama
        """
        try:
            # Step 1: OCR
            latex_result = await Pix2TextService.recognize_formula(problem_file)

            # Step 2: Filter/normalize via Ollama
            filtered_latex = await OllamaService.filter_latex(latex_result)

            return {
                "problem_id": index + 1,
                "filename": problem_file.name,
                "latex_raw": latex_result,
                "latex_filtered": filtered_latex,
                "error": None,
                "success": True
            }
        except Exception as e:
            logger.error(f"OCR/Ollama failed for problem {index + 1}: {str(e)}")
            raise e
