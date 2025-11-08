import cv2
import numpy as np
import logging
from typing import List, Tuple
from fastapi import HTTPException
from app.models.file_model import File

logger = logging.getLogger(__name__)

class WhiteboardProcessorService:
    
    @staticmethod
    async def extract_problems(file: File, padding_ratio: float = 0.1, target_regions: int = 1) -> List[File]:
        """
        Extract mathematical problems from whiteboard image.
        
        Args:
            file: Input image file
            padding_ratio: Padding around detected regions
            target_regions: Number of expressions expected in the image (default: 1)
        
        Returns:
            List of File objects for each detected problem
        """
        try:
            # Convert to OpenCV for processing
            cv2_image = await file.to_cv2()
            
            # Process image with target region count
            problem_regions = await WhiteboardProcessorService._find_text_regions_with_target(
                cv2_image, padding_ratio, target_regions
            )
            
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
            
            logger.info(f"Extracted {len(problem_files)} problems from {file.name} (target: {target_regions})")
            return problem_files
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing whiteboard: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Whiteboard processing failed: {str(e)}")

    @staticmethod
    async def _find_text_regions_with_target(img: np.ndarray, padding_ratio: float, target_regions: int) -> List[np.ndarray]:
        """Find text regions and merge until target count is reached"""
        # Initial text detection
        initial_rects = await WhiteboardProcessorService._detect_text_rectangles(img)
        
        if not initial_rects:
            return []
        
        # If we already have fewer or equal regions than target, return them
        if len(initial_rects) <= target_regions:
            return await WhiteboardProcessorService._extract_regions_from_rects(img, initial_rects, padding_ratio)
        
        # Merge regions until we reach target count
        merged_rects = await WhiteboardProcessorService._merge_to_target_count(initial_rects, target_regions, img.shape)
        
        return await WhiteboardProcessorService._extract_regions_from_rects(img, merged_rects, padding_ratio)

    @staticmethod
    async def _detect_text_rectangles(img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect initial text regions as bounding rectangles"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations to connect text elements
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
        
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return []
        
        h, w = img.shape[:2]
        rects = []
        min_area = (h * w) * 0.0005  # Dynamic minimum area
        
        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area:
                continue
            
            x, y, w_rect, h_rect = cv2.boundingRect(c)
            rects.append((x, y, w_rect, h_rect))
        
        return rects

    @staticmethod
    async def _merge_to_target_count(rects: List[Tuple], target_count: int, img_shape: Tuple) -> List[Tuple]:
        """
        Merge rectangles until we reach the target count by always merging the closest pair
        """
        current_rects = rects.copy()
        h, w = img_shape[:2]
        
        while len(current_rects) > target_count:
            if len(current_rects) <= 1:
                break
            
            # Find the two closest rectangles
            best_distance = float('inf')
            best_pair = (0, 1)
            
            for i in range(len(current_rects)):
                for j in range(i + 1, len(current_rects)):
                    dist = await WhiteboardProcessorService._calculate_rectangle_distance(current_rects[i], current_rects[j], w, h)
                    if dist < best_distance:
                        best_distance = dist
                        best_pair = (i, j)
            
            # Merge the closest pair
            i, j = best_pair
            merged_rect = await WhiteboardProcessorService._merge_two_rectangles(current_rects[i], current_rects[j])
            
            # Remove old rectangles and add merged one
            new_rects = [rect for idx, rect in enumerate(current_rects) if idx not in (i, j)]
            new_rects.append(merged_rect)
            current_rects = new_rects
        
        return current_rects

    @staticmethod
    async def _calculate_rectangle_distance(rect1: Tuple, rect2: Tuple, img_width: int, img_height: int) -> float:
        """
        Calculate distance between two rectangles considering both spatial distance and size similarity
        Lower distance means more likely to be merged
        """
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # Calculate centers
        center1_x, center1_y = x1 + w1/2, y1 + h1/2
        center2_x, center2_y = x2 + w2/2, y2 + h2/2
        
        # Euclidean distance between centers (normalized by image size)
        spatial_distance = np.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)
        spatial_distance /= np.sqrt(img_width**2 + img_height**2)  # Normalize to [0,1]
        
        # Size similarity (rectangles of similar size are more likely to be merged)
        area1 = w1 * h1
        area2 = w2 * h2
        size_similarity = abs(area1 - area2) / max(area1, area2) if max(area1, area2) > 0 else 0
        
        # Aspect ratio similarity
        aspect1 = w1 / h1 if h1 > 0 else 1
        aspect2 = w2 / h2 if h2 > 0 else 1
        aspect_similarity = abs(aspect1 - aspect2) / max(aspect1, aspect2)
        
        # Horizontal alignment (prefer merging horizontally aligned rectangles)
        vertical_overlap = min(y1 + h1, y2 + h2) - max(y1, y2)
        horizontal_alignment = 1 - (vertical_overlap / min(h1, h2)) if min(h1, h2) > 0 else 0
        
        # Combined distance (you can adjust weights based on what works best)
        distance = (
            spatial_distance * 0.5 +
            size_similarity * 0.2 +
            aspect_similarity * 0.1 +
            horizontal_alignment * 0.2
        )
        
        return distance

    @staticmethod
    async def _merge_two_rectangles(rect1: Tuple, rect2: Tuple) -> Tuple:
        """Merge two rectangles into one bounding box"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        new_x = min(x1, x2)
        new_y = min(y1, y2)
        new_w = max(x1 + w1, x2 + w2) - new_x
        new_h = max(y1 + h1, y2 + h2) - new_y
        
        return (new_x, new_y, new_w, new_h)

    @staticmethod
    async def _extract_regions_from_rects(img: np.ndarray, rects: List[Tuple], padding_ratio: float) -> List[np.ndarray]:
        """Extract image regions from bounding rectangles"""
        h, w = img.shape[:2]
        regions = []
        
        for x, y, w_rect, h_rect in rects:
            pad_w = int(w_rect * padding_ratio)
            pad_h = int(h_rect * padding_ratio)
            x1, y1 = max(0, x - pad_w), max(0, y - pad_h)
            x2, y2 = min(w, x + w_rect + pad_w), min(h, y + h_rect + pad_h)
            
            region = img[y1:y2, x1:x2]
            regions.append(region)
        
        return regions