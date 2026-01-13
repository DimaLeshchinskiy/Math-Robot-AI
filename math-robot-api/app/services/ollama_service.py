import aiohttp
import asyncio
import logging
from fastapi import HTTPException
from app.config import config
import re

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
        
        # Clean the latex_input before inserting into prompt
        latex_cleaned = latex_input.strip()
        # Remove trailing '=' if present (also handle cases with spaces)
        latex_cleaned = re.sub(r'\s*=*\s*$', '', latex_cleaned)
        # Remove backslashes not followed by letters
        latex_cleaned = re.sub(r'\\(?![a-zA-Z])', '', latex_cleaned)  

        # Check if it's an equation (contains equation/inequality symbols)
        # This pattern looks for =, <, >, ≤, ≥, ≠ in the middle of the expression
        # (not just at the very end which might be a typo)
        equation_pattern = r'[=<>≤≥≠]'
        is_equation = bool(re.search(equation_pattern, latex_cleaned))
    
        # Choose prompt based on whether it's an equation or not
        if is_equation:
            strict_prompt = f"""CONVERT EQUATION LaTeX TO WOLFRAM LANGUAGE SYNTAX

            CRITICAL RULES:
            1. Output ONLY the Wolfram code, no explanations, no markdown, no extra text
            2. The input is an equation/inequality (contains =, <, >, etc.)
            3. Wrap the expression in Solve[], Reduce[], or appropriate equation-solving function
            4. Use == for equations inside Solve[]/Reduce[] (Wolfram uses double equals)
            5. Remove any trailing = signs from the expression
            6. Include the variable to solve for if not obvious

            EXAMPLES:
            - "x^2 + 2x + 1 = 0" → "Solve[x^2 + 2*x + 1 == 0, x]"
            - "2x + 3 > 7" → "Solve[2*x + 3 > 7, x]"
            - "a^2 = b^2 + c^2" → "Solve[a^2 == b^2 + c^2, a]"

            Input: {latex_cleaned}

            Wolfram Language code:"""
        else:
            strict_prompt = f"""CONVERT EXPRESSION LaTeX TO WOLFRAM LANGUAGE SYNTAX

            CRITICAL RULES:
            1. Output ONLY the Wolfram code, no explanations, no markdown, no extra text
            2. The input is a mathematical expression (NOT an equation - no =, <, >, etc.)
            3. Convert directly to Wolfram syntax without Solve[] or Reduce[]
            4. For limits use Limit[]
            5. For integrals use Integrate[]
            6. For derivatives use D[] or Derivative[]
            7. Convert LaTeX symbols: π → Pi, ∞ → Infinity, etc.

            EXAMPLES:
            - "x^2 + 2x + 1" → "x^2 + 2*x + 1"
            - "\\int x^2 dx" → "Integrate[x^2, x]"

            Input: {latex_cleaned}

            Wolfram Language code:"""

        

        model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
        
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

    @staticmethod
    async def filter_result(latex_input: str, wolfram_input: str) -> str:
        """
        Send Wolfram result to the Ollama model and get back a filtered version.
        """
        if not wolfram_input.strip():
            raise HTTPException(status_code=400, detail="Empty Wolfram input")

        model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
    
        strict_prompt = f"""Your task is to convert Wolfram computation results into a natural English sentence for a robot to speak. 
Return ONLY the final spoken sentence, nothing else. Say constants as words like pi, euler number... Do not print in unicode.

Wolfram Task: {latex_input.strip()}
Wolfram Result: {wolfram_input.strip()}"""
        
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

