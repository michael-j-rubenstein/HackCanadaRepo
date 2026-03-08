import asyncio
import time
from typing import Optional

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from app.config import settings

_client: Optional[genai.Client] = None

FLASH = "gemini-2.5-flash"


def get_client() -> genai.Client:
    """Lazy-load the Gemini client."""
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client
FLASH_LITE = "gemini-2.5-flash-lite"
PRO = "gemini-2.5-pro"


def generate(prompt: str, model: str = FLASH, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = get_client().models.generate_content(model=model, contents=prompt)
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
                get_client().models.generate_content, model=model, contents=prompt
            )
            return response.text
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s before retry...")
                await asyncio.sleep(wait)
            else:
                raise


def generate_structured(
    contents: list,
    response_schema: dict,
    response_mime_type: str = "application/json",
    model: str = FLASH,
    max_retries: int = 3,
) -> str:
    for attempt in range(max_retries):
        try:
            response = get_client().models.generate_content(
                model=model,
                contents=contents,
                config={
                    "response_mime_type": response_mime_type,
                    "response_schema": response_schema,
                },
            )
            return response.text
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise


async def generate_structured_async(
    contents: list,
    response_schema: dict,
    response_mime_type: str = "application/json",
    model: str = FLASH,
    max_retries: int = 3,
) -> str:
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                get_client().models.generate_content,
                model=model,
                contents=contents,
                config={
                    "response_mime_type": response_mime_type,
                    "response_schema": response_schema,
                },
            )
            return response.text
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s before retry...")
                await asyncio.sleep(wait)
            else:
                raise
