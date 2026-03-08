import socketio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import example, items, receipts
from app.sockets.recipe_socket import sio


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(example.router, prefix=settings.API_V1_STR)
app.include_router(items.router, prefix=settings.API_V1_STR)
app.include_router(receipts.router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok"}


socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
