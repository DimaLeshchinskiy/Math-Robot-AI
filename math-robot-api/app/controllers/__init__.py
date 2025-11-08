from fastapi import APIRouter
from app.controllers import pix2text_controller
from app.controllers import whiteboard_processor_controller
from app.controllers import pipeline_controller
from app.controllers import status_controller
from app.controllers import test_controller

router = APIRouter()

router.include_router(pix2text_controller.router, tags=["Picture to Text"])
router.include_router(whiteboard_processor_controller.router, tags=["Whiteboard processor"])
router.include_router(pipeline_controller.router, tags=["Pipeline"])
router.include_router(status_controller.router, tags=["Status"])
router.include_router(test_controller.router, tags=["Test"])