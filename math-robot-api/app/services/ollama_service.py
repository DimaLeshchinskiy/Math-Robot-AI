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
                "model": "qwen2.5:7b",
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
        # Remove spaces between numbers
        latex_cleaned = re.sub(r'(\d)(\s+)(?=\d)', r'\1', latex_cleaned)

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
            3. Wrap the expression in Reduce[], or appropriate equation-solving function
            4. Use == for equations inside Reduce[] (Wolfram uses double equals)
            5. Remove any trailing = signs from the expression
            6. Include the variable to solve for if not obvious

            EXAMPLES:
            - "x^2 + 2x + 1 = 0" → "Reduce[x^2 + 2*x + 1 == 0, x]"
            - "2x + 3 > 7" → "Reduce[2*x + 3 > 7, x]"
            - "a^2 = b^2 + c^2" → "Reduce[a^2 == b^2 + c^2, a]"

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
            - "frac [3] [4] → "3 / 4"

            Input: {latex_cleaned}

            Wolfram Language code:"""

        

        model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
        
        payload = {
            "model": "qwen2.5:7b",
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
        Supports both English (en) and Czech (cz) languages.
        """
        if not wolfram_input.strip():
            raise HTTPException(status_code=400, detail="Empty Wolfram input")

        model_url = f"{config.OLLAMA_URL.rstrip('/')}/api/generate"
        lang = config.OLLAMA_LANG.lower()  # en, cz
        
        # Define language-specific prompts
        prompts = {
            "en": {
                "prompt": """TASK: Convert Wolfram computation results into natural English speech for a robot voice.

    CRITICAL RULES:
    1. Return ONLY the final spoken sentence, nothing else
    2. Do not include prefixes like "Robot says:" or "The result is:"
    3. Speak constants as words: π → "pi", e → "Euler's number", ∞ → "infinity"
    4. Keep numbers as digits: 3.14159 → "3 point 1 4 1 5 9" (speak each digit)
    5. No Unicode symbols - use words instead

    EXAMPLES:
    Input: Task: Limit[x/Sin[x], x->0], Result: 1
    Output: 1.

    Input: Task: Integrate[x^2, [x, 0, 1]], Result: 1/3
    Output: result is one third.

    Input: Task: Sum[1/n^2, [n, 1, Infinity]], Result: π^2/6
    Output: pi squared over 6.

    Input: Result: Cos[x]
    Output: Result is cosine of x.

    Input: Result: 4
    Output: Result is 4

    INPUT TO CONVERT:
    Wolfram Result: {wolfram_input}

    SPOKEN SENTENCE (output ONLY this):"""
            },
            "cz": {
                "prompt": """ÚKOL: Převeď výsledky z Wolframu do přirozené češtiny pro hlas robota.

    KRITICKÁ PRAVIDLA:
    1. Vrať POUZE výslednou větu k odmluvení, nic jiného
    2. Nepřidávej předpony jako "Robot říká:" nebo "Výsledek je:"
    3. Konstanty převáděj na slova: π → "pí", e → "Eulerovo číslo", ∞ → "nekonečno"
    4. Čísla nech jako číslice: 3,14159 → "3 celá 1 4 1 5 9" (vyřkni každou číslici)
    5. Žádné Unicode symboly - místo nich použij slova

    PŘÍKLADY:
    Vstup: Úloha: Limit[x/Sin[x], x->0], Výsledek: 1
    Výstup: 1.

    Vstup: Úloha: Integrate[x^2, [x, 0, 1]], Výsledek: 1/3
    Výstup: výsledek je jedna třetina.

    Vstup: Úloha: Sum[1/n^2, [n, 1, Infinity]], Výsledek: π^2/6
    Výstup: pí na druhou lomeno 6.

    Vstup: Výsledek: Cos[x]
    Výstup: Výsledek je cosinus x.

    Vstup: Výsledek: 4
    Výstup: Výsledek je 4

    VSTUP KE ZPRACOVÁNÍ:
    Wolfram Výsledek: {wolfram_input}

    VĚTA K ODMLUVENÍ (vrať POUZE toto):"""
            }
        }
        
        # Get the appropriate prompt for the current language
        if lang not in prompts:
            logger.warning(f"Unsupported language: {lang}, defaulting to English")
            lang = "en"
        
        prompt_config = prompts[lang]
        strict_prompt = prompt_config["prompt"].format(wolfram_input=wolfram_input.strip())
        
        payload = {
            "model": "qwen2.5:7b",
            "prompt": strict_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 100,
                "stop": ["\n\n", "Explanation:", "Note:", "Vysvětlení:", "Poznámka:"]  # Bilingual stop sequences
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
