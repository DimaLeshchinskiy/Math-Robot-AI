import logging
from fastapi import UploadFile, HTTPException
from app.models.file_model import File

logger = logging.getLogger(__name__)

class FileService:
    """Simple file service for validation and basic operations"""
    
    SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    async def validate_and_convert(uploaded_file: UploadFile) -> File:
        """
        Validate uploaded file and convert to internal File model.
        This is the ONLY method controllers should call.
        """
        try:
            # Basic validation
            if not uploaded_file or not uploaded_file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Read content
            content = await uploaded_file.read()
            
            # Validate size
            if len(content) > FileService.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File too large. Max: {FileService.MAX_FILE_SIZE // (1024*1024)}MB")
            
            # Validate extension
            file_ext = '.' + uploaded_file.filename.split('.')[-1].lower() if '.' in uploaded_file.filename else ''
            if file_ext not in FileService.SUPPORTED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {', '.join(FileService.SUPPORTED_EXTENSIONS)}")
            
            # Create internal file model
            internal_file = File(
                name=uploaded_file.filename,
                data=content,
                data_type='bytes'
            )
            
            logger.info(f"Validated file: {uploaded_file.filename}")
            return internal_file
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")