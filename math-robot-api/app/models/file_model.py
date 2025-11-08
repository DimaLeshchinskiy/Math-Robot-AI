from typing import Union
import io
from PIL import Image
import numpy as np
import cv2

class File:
    """
    Unified file representation for internal use.
    Contains the raw data and metadata that services can work with.
    """
    def __init__(self, name: str, data: Union[bytes, Image.Image, np.ndarray], data_type: str):
        self.name = name
        self.data = data
        self.data_type = data_type  # 'bytes', 'pil', 'cv2'
    
    async def to_pil(self) -> Image.Image:
        """Convert to PIL Image"""
        if self.data_type == 'pil':
            return self.data
        elif self.data_type == 'bytes':
            return Image.open(io.BytesIO(self.data))
        elif self.data_type == 'cv2':
            # Convert BGR to RGB
            if len(self.data.shape) == 3 and self.data.shape[2] == 3:
                rgb_data = cv2.cvtColor(self.data, cv2.COLOR_BGR2RGB)
            else:
                rgb_data = self.data
            return Image.fromarray(rgb_data)
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")
    
    async def to_cv2(self) -> np.ndarray:
        """Convert to OpenCV format (BGR)"""
        if self.data_type == 'cv2':
            return self.data
        elif self.data_type == 'pil':
            img_array = np.array(self.data)
            # Convert RGB to BGR
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            return img_array
        elif self.data_type == 'bytes':
            pil_img = await self.to_pil()
            return await File(name=self.name, data=pil_img, data_type='pil').to_cv2()
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")
    
    async def to_bytes(self) -> bytes:
        """Convert to bytes"""
        if self.data_type == 'bytes':
            return self.data
        elif self.data_type == 'pil':
            buffer = io.BytesIO()
            self.data.save(buffer, format='PNG')
            return buffer.getvalue()
        elif self.data_type == 'cv2':
            pil_img = await self.to_pil()
            return await File(name=self.name, data=pil_img, data_type='pil').to_bytes()
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")