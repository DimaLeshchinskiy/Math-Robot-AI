import aiohttp
import logging
from urllib.parse import quote
from fastapi import HTTPException
from app.config import config

logger = logging.getLogger(__name__)


class WolframService:
    @staticmethod
    async def calculate(latex_input: str) -> str:
        """Calculate result using Wolfram Alpha proxy."""
        if not latex_input.strip():
            raise HTTPException(status_code=400, detail="Empty LaTeX input")

        # URL encode the LaTeX input to handle special characters
        encoded_latex = quote(latex_input)
        wolfram_url = f"{config.WOLFRAM_URL.rstrip('/')}/eval?code={encoded_latex}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(wolfram_url) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error(f"Wolfram proxy error {response.status}: {text}")
                        
                        if response.status == 400:
                            raise HTTPException(
                                status_code=400,
                                detail="Invalid input format"
                            )
                        elif response.status == 500:
                            raise HTTPException(
                                status_code=500,
                                detail="Wolfram computation failed"
                            )
                        else:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Wolfram service returned {response.status}"
                            )

                    # Parse the JSON response
                    data = await response.json()
                    
                    # Check for error in response
                    if 'error' in data:
                        logger.error(f"Wolfram computation error: {data['error']}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Wolfram computation error: {data['error']}"
                        )
                    
                    # Get the result (based on your proxy returning {'result': '...'})
                    result = data.get('result', '').strip()
                    
                    if not result:
                        raise HTTPException(
                            status_code=500,
                            detail="Wolfram returned an empty result"
                        )

                    return result

        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to Wolfram proxy: {e}")
            raise HTTPException(status_code=503, detail=f"Wolfram proxy unreachable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in WolframService: {e}")
            raise HTTPException(status_code=500, detail=f"Wolfram request failed: {e}")