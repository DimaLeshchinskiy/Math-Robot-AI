import aiohttp
import asyncio
import logging
from fastapi import HTTPException
from app.config import config

logger = logging.getLogger(__name__)


class OllamaService:
    __instance = None
    __lock = asyncio.Lock()
    __is_warmed_up = False

    @classmethod
    async def get_instance(cls):
        """Return the singleton instance."""
        async with cls.__lock:
            if cls.__instance is None:
                cls.__instance = OllamaService()
            return cls.__instance

    @classmethod
    async def init(cls) -> None:
        """Warm up the Ollama model (only once)."""
        async with cls.__lock:
            if cls.__is_warmed_up:
                return

            logger.info("🔄 Warming up Ollama model qwen2.5:3b...")

            model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
            payload = {
                "model": "qwen2.5:3b",
                "prompt": "warmup",
                "stream": False,
                "options": {"num_predict": 1}
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(model_url, json=payload) as response:
                        if response.status != 200:
                            text = await response.text()
                            logger.error(
                                f"Ollama warmup error {response.status}: {text}"
                            )
                            return

                        await response.json()

                cls.__is_warmed_up = True
                logger.info("✅ Ollama warm-up completed successfully.")

            except Exception as e:
                logger.error(f"Ollama warmup failed: {e}")

    @staticmethod
    async def filter_latex(latex_input: str) -> str:
        """Call Ollama API to convert LaTeX → Wolfram Alpha syntax."""
        if not latex_input.strip():
            raise HTTPException(status_code=400, detail="Empty LaTeX input")

        model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
    
        strict_prompt = f"""Convert this LaTeX math expression to Wolfram Alpha syntax. 
CRITICAL: Output ONLY the Wolfram code, no explanations, no descriptions, no text.
ONLY output valid Wolfram Alpha syntax.

Input: {latex_input.strip()}

Output:"""
        
        payload = {
            "model": "qwen2.5:3b",
            "prompt": strict_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 100,
                "stop": ["\n\n", "Explanation:", "Note:"]
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
