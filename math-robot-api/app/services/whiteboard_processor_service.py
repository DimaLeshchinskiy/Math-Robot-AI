import cv2
import numpy as np
import logging
from typing import List
from fastapi import HTTPException
from app.models.file_model import File

logger = logging.getLogger(__name__)

class WhiteboardProcessorService:
    
    @staticmethod
    async def extract_problems(file: File, padding_ratio: float = 0.1) -> List[File]:
        """
        Extract mathematical problems from whiteboard image.
        Returns list of File objects for each detected problem.
        """
        try:
            # Convert to OpenCV for processing
            cv2_image = await file.to_cv2()
            
            # Process image
            problem_regions = await WhiteboardProcessorService._find_text_regions(cv2_image, padding_ratio)
            
            if not problem_regions:
                raise HTTPException(status_code=400, detail="No mathematical problems detected")
            
            # Convert regions to File objects
            problem_files = []
            for i, region in enumerate(problem_regions):
                problem_file = File(
                    name=f"{file.name}_problem_{i+1:02d}",
                    data=region,
                    data_type='cv2'
                )
                problem_files.append(problem_file)
            
            logger.info(f"Extracted {len(problem_files)} problems from {file.name}")
            return problem_files
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing whiteboard: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Whiteboard processing failed: {str(e)}")

    @staticmethod
    async def _find_text_regions(img: np.ndarray, padding_ratio: float) -> List[np.ndarray]:
        """Find text regions in image"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=10)
        
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return []
        
        h_img, w_img = img.shape[:2]
        regions = []
        
        for c in contours:
            area = cv2.contourArea(c)
            if area < 500:
                continue
            
            x, y, w, h = cv2.boundingRect(c)
            pad_w = int(w * padding_ratio)
            pad_h = int(h * padding_ratio)
            x1, y1 = max(0, x - pad_w), max(0, y - pad_h)
            x2, y2 = min(w_img, x + w + pad_w), min(h_img, y + h + pad_h)
            
            region = img[y1:y2, x1:x2]
            regions.append(region)
        
        return regions