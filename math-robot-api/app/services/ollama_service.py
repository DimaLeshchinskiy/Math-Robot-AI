import aiohttp
import logging
from fastapi import HTTPException
from app.config import config

logger = logging.getLogger(__name__)

class OllamaService:
    """
    Service for calling the Ollama API to filter or refine LaTeX problems.
    """

    @staticmethod
    async def filter_latex(latex_input: str) -> str:
        """
        Send LaTeX text to the Ollama model and get back a filtered version.
        """
        if not latex_input.strip():
            raise HTTPException(status_code=400, detail="Empty LaTeX input")

        model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
    
        strict_prompt = f"""Convert this LaTeX math expression to Wolfram Alpha syntax. 
            CRITICAL: Output ONLY the Wolfram code, no explanations, no descriptions, no text.
            ONLY output valid Wolfram Alpha syntax. No other text.

            Input: {latex_input.strip()}

            Output:"""
        
        payload = {
            "model": "qwen2.5:3b",
            "prompt": strict_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Lower temperature for more deterministic output
                "num_predict": 100,
                "stop": ["\n\n", "Explanation:", "Note:"]  # Stop sequences to prevent explanations
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(model_url, json=payload) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error(f"Ollama error {response.status}: {text}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Ollama service returned {response.status}"
                        )

                    data = await response.json()
                    filtered = data.get("response", "").strip()

                    if not filtered:
                        raise HTTPException(
                            status_code=500,
                            detail="Ollama returned an empty response"
                        )

                    return filtered

        except Exception as e:
            logger.error(f"Failed to call Ollama service: {e}")
            raise HTTPException(status_code=500, detail=f"Ollama request failed: {e}")
