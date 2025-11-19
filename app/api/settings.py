from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from orchestrator import scheduler

router = APIRouter()


class SchedulerSettings(BaseModel):
    strategy: str


@router.get("/scheduler")
def get_scheduler_settings():
    return {
        "strategy": scheduler.get_strategy(),
        "available_strategies": ["first_fit", "round_robin", "resource_aware"]
    }


@router.put("/scheduler")
def update_scheduler_settings(settings: SchedulerSettings):
    try:
        scheduler.set_strategy(settings.strategy)
        return {
            "strategy": scheduler.get_strategy(),
            "message": f"Scheduler strategy updated to {settings.strategy}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
