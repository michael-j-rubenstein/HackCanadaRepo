import asyncio
import time

from google import genai
from google.genai.errors import ClientError

from app.config import settings

client = genai.Client(api_key=settings.gemeni_api_key)

FLASH = "gemini-2.5-flash"
FLASH_LITE = "gemini-2.5-flash-lite"
PRO = "gemini-2.5-pro"


def generate(prompt: str, model: str = FLASH, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise


async def generate_async(prompt: str, model: str = FLASH, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                client.models.generate_content, model=model, contents=prompt
            )
            return response.text
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s before retry...")
                await asyncio.sleep(wait)
            else:
                raise
