from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        logger.info(f"Incoming request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            logger.info(
                f"Request completed: {request.method} {request.url} - "
                f"Status: {response.status_code}"
            )
            return response
        except Exception as e:
            logger.error(
                f"Request failed: {request.method} {request.url} - "
                f"Error: {str(e)}"
            )
            raise