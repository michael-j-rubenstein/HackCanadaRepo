import base64
import json
import re

import httpx
from tavily import AsyncTavilyClient
import google.generativeai as genai

from app.config import settings

genai.configure(api_key=settings.gemeni_api_key)


async def search_recipe(ingredients: list[str]) -> str:
    client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    query = f"recipe using {', '.join(ingredients)} with step by step instructions"
    response = await client.search(query, max_results=3, include_raw_content=True)
    parts = []
    for result in response.get("results", []):
        raw = result.get("raw_content") or result.get("content", "")
        if raw:
            parts.append(raw[:3000])
    return "\n\n---\n\n".join(parts) if parts else ""


async def parse_recipe_steps(raw_text: str, ingredients: list[str]) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""You are a recipe parser. Given the following raw recipe text and the user's available ingredients, extract a structured recipe.

User's ingredients: {', '.join(ingredients)}

Raw recipe text:
{raw_text[:6000]}

Return ONLY valid JSON (no markdown fences) in this exact format:
{{
  "title": "Recipe Title",
  "summary": "Brief 1-2 sentence summary",
  "steps": [
    {{
      "title": "Step title",
      "instruction": "Detailed instruction for this step. Write 2-3 sentences."
    }}
  ]
}}

Extract between 4-8 clear cooking steps. Each step instruction should be specific and actionable."""

    response = await model.generate_content_async(prompt)
    text = response.text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def generate_tts(text: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode("utf-8")
