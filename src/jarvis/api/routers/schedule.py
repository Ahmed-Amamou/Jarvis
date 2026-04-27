from fastapi import APIRouter
from pydantic import BaseModel

from src.jarvis.scheduler.jobs import email_check, meeting_reminder, morning_summary

router = APIRouter(prefix="/schedules")

# In-memory job registry (will be backed by APScheduler in lifespan)
_scheduler = None


def set_scheduler(scheduler):
    global _scheduler
    _scheduler = scheduler


class ScheduleCreate(BaseModel):
    name: str
    cron: str  # cron expression, e.g. "0 8 * * *"
    job_type: str  # morning_summary, meeting_reminder, email_check


class ScheduleResponse(BaseModel):
    id: str
    name: str
    next_run: str | None


JOB_MAP = {
    "morning_summary": morning_summary,
    "meeting_reminder": meeting_reminder,
    "email_check": email_check,
}


@router.get("")
async def list_schedules():
    if not _scheduler:
        return []
    jobs = _scheduler.get_jobs()
    return [
        {"id": job.id, "name": job.name, "next_run": str(job.next_run_time)}
        for job in jobs
    ]


@router.post("")
async def create_schedule(req: ScheduleCreate):
    if not _scheduler:
        return {"error": "Scheduler not initialized"}

    func = JOB_MAP.get(req.job_type)
    if not func:
        return {"error": f"Unknown job type: {req.job_type}. Valid: {list(JOB_MAP.keys())}"}

    # Parse cron expression (minute hour day month day_of_week)
    parts = req.cron.split()
    if len(parts) != 5:
        return {"error": "Invalid cron expression. Expected 5 fields: min hour day month dow"}

    _scheduler.add_job(
        func,
        "cron",
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
        id=req.name,
        name=req.name,
        replace_existing=True,
    )
    return {"status": "created", "name": req.name, "cron": req.cron}


@router.delete("/{job_id}")
async def delete_schedule(job_id: str):
    if not _scheduler:
        return {"error": "Scheduler not initialized"}
    try:
        _scheduler.remove_job(job_id)
        return {"status": "deleted", "id": job_id}
    except Exception as e:
        return {"error": str(e)}
