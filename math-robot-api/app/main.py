from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging

from app.schemas.error_schema import ErrorResponse
from app.middlewares.log_middleware import LogMiddleware
from app.services.pix2text_service import Pix2TextService
from app.services.ollama_service import OllamaService
from app.services.whiteboard_processor_service import WhiteboardProcessorService

def create_app() -> FastAPI:
    # Initialize FastAPI
    app = FastAPI(
        title="Math Robot API",
        description="Handwritten Mathematical Problem Recognition",
        version="1.0.0",
        responses={
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            400: {"model": ErrorResponse, "description": "Bad Request"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        }
    )

    # Add Prometheus metrics
    Instrumentator().instrument(app).expose(app)

    # Custom middleware for logging
    app.add_middleware(LogMiddleware)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.on_event("startup")
    async def startup_event():     
        pix2text_service = await Pix2TextService.get_instance()
        await pix2text_service.init()

        ollama_service = await OllamaService.get_instance()
        await ollama_service.init()

        whiteboard_processor_service = await WhiteboardProcessorService.get_instance()
        await whiteboard_processor_service.init()

        from app.controllers import router
        # Include routers
        app.include_router(router)

    return app

app = create_app()