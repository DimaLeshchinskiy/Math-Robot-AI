import asyncio
import logging
from pix2text import Pix2Text
from app.models.file_model import File

logger = logging.getLogger(__name__)

class Pix2TextService:
    __instance = None
    __lock = asyncio.Lock()
    __model = None

    @classmethod
    async def get_instance(cls):
        async with cls.__lock:
            if not cls.__instance:
                cls.__instance = Pix2TextService()
        return cls.__instance

    @classmethod
    async def init(cls):
        async with cls.__lock:
            if not cls.__model:
                logger.info("Loading Pix2Text model...")
                cls.__model = Pix2Text.from_config()
                logger.info("Pix2Text model loaded successfully")

    @staticmethod
    async def recognize_formula(file: File) -> str:
        """Recognize formula from File model"""
        if not Pix2TextService.__model:
            raise Exception("Pix2Text model not initialized. Call init() first.")
        
        try:
            # Convert to PIL (what Pix2Text expects)
            pil_image = await file.to_pil()
            
            # Recognize formula
            latex_text = Pix2TextService.__model.recognize_formula(pil_image)
            
            logger.info(f"Successfully recognized formula from {file.name}")
            return latex_text
            
        except Exception as e:
            logger.error(f"Error recognizing formula: {str(e)}")
            raise Exception(f"Failed to recognize formula: {str(e)}")