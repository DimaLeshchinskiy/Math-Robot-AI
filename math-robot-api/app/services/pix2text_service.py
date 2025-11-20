import asyncio
import logging
from PIL import Image
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq
from app.models.file_model import File

logger = logging.getLogger(__name__)

MODEL_NAME = "breezedeus/pix2text-mfr-1.5"


class Pix2TextService:
    __instance = None
    __lock = asyncio.Lock()
    __processor = None
    __model = None

    @classmethod 
    async def get_instance(cls): 
        async with cls.__lock: 
            if not cls.__instance: 
                cls.__instance = Pix2TextService() 
                return cls.__instance

    @classmethod
    async def init(cls):
        """Load the ONNX model & processor once."""
        async with cls.__lock:
            if cls.__model is not None:
                return

            logger.info("Loading Pix2Text ONNX model...")

            cls.__processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
            cls.__model = ORTModelForVision2Seq.from_pretrained(
                MODEL_NAME,
                use_cache=False
            )

            logger.info("Pix2Text ONNX model loaded successfully")

    @staticmethod
    async def recognize_formula(file: File) -> str:
        """Extract LaTeX from a mathematical image."""
        if Pix2TextService.__model is None:
            raise Exception("Pix2TextService not initialized. Call init() first.")

        try:
            # Your File model returns a PIL image
            pil_image: Image.Image = await file.to_pil()
            pil_image = pil_image.convert("RGB")

            # Convert to tensor for ONNX
            pixel_values = Pix2TextService.__processor(
                images=[pil_image],
                return_tensors="pt"
            ).pixel_values

            # Generate predicted LaTeX
            generated_ids = Pix2TextService.__model.generate(pixel_values)

            # Decode tokens into text
            text = Pix2TextService.__processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]

            logger.info(f"Recognized LaTeX from {file.name}: {text}")
            return text

        except Exception as e:
            logger.error(f"Failed LaTeX OCR: {str(e)}")
            raise Exception(f"Failed LaTeX OCR: {str(e)}")
