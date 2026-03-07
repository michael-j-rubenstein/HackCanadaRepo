import asyncio
import re

import socketio

from app.config import settings
from app.services.recipe_service import search_recipe, parse_recipe_steps, generate_tts

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

sessions: dict[str, dict] = {}


def get_session(sid: str) -> dict:
    if sid not in sessions:
        sessions[sid] = {
            "steps": [],
            "current_step": 0,
            "idle_task": None,
            "audio_cache": {},
            "recipe": None,
        }
    return sessions[sid]


def cancel_idle(session: dict):
    task = session.get("idle_task")
    if task and not task.done():
        task.cancel()
    session["idle_task"] = None


async def start_idle_timer(sid: str, session: dict):
    cancel_idle(session)

    async def _nudge():
        await asyncio.sleep(settings.IDLE_TIMEOUT_SECONDS)
        if sid in sessions:
            try:
                audio = await generate_tts("Are you still there? Let me know when you're ready to continue.")
                await sio.emit("nudge", {
                    "message": "Are you still there? Let me know when you're ready to continue.",
                    "audio_base64": audio,
                }, to=sid)
            except Exception:
                await sio.emit("nudge", {
                    "message": "Are you still there? Let me know when you're ready to continue.",
                    "audio_base64": "",
                }, to=sid)

    session["idle_task"] = asyncio.create_task(_nudge())


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]


async def send_step(sid: str, session: dict, step_index: int):
    cancel_idle(session)
    steps = session["steps"]
    if step_index < 0 or step_index >= len(steps):
        return
    session["current_step"] = step_index
    step = steps[step_index]
    total = len(steps)

    await sio.emit("step_start", {
        "step_number": step_index + 1,
        "total_steps": total,
        "title": step["title"],
    }, to=sid)

    instruction = step["instruction"]

    # Stream text word-by-word and generate audio concurrently
    async def stream_text():
        words = instruction.split()
        chunk = []
        for w in words:
            chunk.append(w)
            if len(chunk) >= 3:
                await sio.emit("step_text", {"text": " ".join(chunk) + " "}, to=sid)
                chunk = []
                await asyncio.sleep(0.05)
        if chunk:
            await sio.emit("step_text", {"text": " ".join(chunk)}, to=sid)

    async def generate_audio():
        sentences = split_sentences(instruction)
        cache_key = step_index
        if cache_key not in session["audio_cache"]:
            session["audio_cache"][cache_key] = {}
        for i, sentence in enumerate(sentences):
            if i in session["audio_cache"][cache_key]:
                audio_b64 = session["audio_cache"][cache_key][i]
            else:
                try:
                    audio_b64 = await generate_tts(sentence)
                except Exception:
                    audio_b64 = ""
                session["audio_cache"][cache_key][i] = audio_b64
            await sio.emit("step_audio", {
                "audio_base64": audio_b64,
                "sentence_index": i,
            }, to=sid)

    await asyncio.gather(stream_text(), generate_audio())

    await sio.emit("step_end", {}, to=sid)

    # Pre-cache next step audio in background
    if step_index + 1 < total:
        asyncio.create_task(precache_audio(session, step_index + 1))

    await start_idle_timer(sid, session)


async def precache_audio(session: dict, step_index: int):
    if step_index >= len(session["steps"]):
        return
    step = session["steps"][step_index]
    sentences = split_sentences(step["instruction"])
    if step_index not in session["audio_cache"]:
        session["audio_cache"][step_index] = {}
    for i, sentence in enumerate(sentences):
        if i not in session["audio_cache"][step_index]:
            try:
                session["audio_cache"][step_index][i] = await generate_tts(sentence)
            except Exception:
                pass


@sio.event
async def connect(sid, environ):
    pass


@sio.event
async def disconnect(sid):
    session = sessions.pop(sid, None)
    if session:
        cancel_idle(session)


@sio.on("start_recipe")
async def handle_start_recipe(sid, data):
    session = get_session(sid)
    ingredients = data.get("ingredients", [])
    if not ingredients:
        await sio.emit("error", {"message": "No ingredients provided."}, to=sid)
        return

    try:
        await sio.emit("status", {"message": "Searching for recipes..."}, to=sid)
        raw_text = await search_recipe(ingredients)
        if not raw_text:
            await sio.emit("error", {"message": "Could not find a recipe with those ingredients."}, to=sid)
            return

        await sio.emit("status", {"message": "Parsing recipe steps..."}, to=sid)
        recipe = await parse_recipe_steps(raw_text, ingredients)
        session["recipe"] = recipe
        session["steps"] = recipe.get("steps", [])
        session["current_step"] = 0
        session["audio_cache"] = {}

        await sio.emit("recipe_found", {
            "title": recipe.get("title", "Recipe"),
            "total_steps": len(session["steps"]),
            "summary": recipe.get("summary", ""),
        }, to=sid)

        if session["steps"]:
            await sio.emit("status", {"message": "Generating voice narration..."}, to=sid)
            await send_step(sid, session, 0)

    except Exception as e:
        await sio.emit("error", {"message": f"Something went wrong: {str(e)}"}, to=sid)


@sio.on("step_complete")
async def handle_step_complete(sid, data=None):
    session = sessions.get(sid)
    if not session:
        return
    cancel_idle(session)
    next_step = session["current_step"] + 1
    if next_step >= len(session["steps"]):
        try:
            audio = await generate_tts("Congratulations! You've completed the recipe. Enjoy your meal!")
        except Exception:
            audio = ""
        await sio.emit("recipe_complete", {
            "message": "Congratulations! You've completed the recipe. Enjoy your meal!",
            "audio_base64": audio,
        }, to=sid)
    else:
        await send_step(sid, session, next_step)


@sio.on("repeat")
async def handle_repeat(sid, data=None):
    session = sessions.get(sid)
    if not session:
        return
    cancel_idle(session)
    await send_step(sid, session, session["current_step"])


@sio.on("skip")
async def handle_skip(sid, data=None):
    session = sessions.get(sid)
    if not session:
        return
    cancel_idle(session)
    next_step = session["current_step"] + 1
    if next_step >= len(session["steps"]):
        try:
            audio = await generate_tts("Congratulations! You've completed the recipe. Enjoy your meal!")
        except Exception:
            audio = ""
        await sio.emit("recipe_complete", {
            "message": "Congratulations! You've completed the recipe. Enjoy your meal!",
            "audio_base64": audio,
        }, to=sid)
    else:
        await send_step(sid, session, next_step)


@sio.on("go_back")
async def handle_go_back(sid, data=None):
    session = sessions.get(sid)
    if not session:
        return
    cancel_idle(session)
    prev_step = max(0, session["current_step"] - 1)
    await send_step(sid, session, prev_step)
