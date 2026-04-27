import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from src.jarvis.api.routers import auth, chat, health, schedule
from src.jarvis.scheduler.jobs import email_check, meeting_reminder, morning_summary

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — initialize scheduler with default jobs
    scheduler = AsyncIOScheduler()

    # Default jobs
    scheduler.add_job(morning_summary, "cron", hour=8, minute=0, id="morning_summary", name="morning_summary")
    scheduler.add_job(meeting_reminder, "cron", minute="*/5", id="meeting_reminder", name="meeting_reminder")
    scheduler.add_job(email_check, "cron", minute="*/30", id="email_check", name="email_check")

    scheduler.start()
    schedule.set_scheduler(scheduler)
    logger.info("Scheduler started with default jobs")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)

    from src.jarvis.api.deps import get_llm_gateway
    gateway = get_llm_gateway()
    for provider, _ in gateway.router.resolve("default"):
        if hasattr(provider, "close"):
            await provider.close()


app = FastAPI(
    title="JARVIS",
    description="AI Assistant with Gmail & Calendar integration",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(schedule.router)
