import logging
import socketio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.routes import example, items, receipts
from app.sockets.recipe_socket import sio
from app.jobs.price_aggregation import aggregate_hourly_prices

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run hourly from 8am to 1am (hours: 0,1,8-23)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        aggregate_hourly_prices,
        CronTrigger(hour="0,1,8-23", minute=0),
        id="hourly_price_aggregation",
        name="Aggregate hourly prices",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Price aggregation scheduler started (runs hourly 8am–1am)")
    yield
    scheduler.shutdown()
    logger.info("Price aggregation scheduler stopped")


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
