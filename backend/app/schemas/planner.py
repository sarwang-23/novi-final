import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class DailyCheckinSave(BaseModel):
    date: datetime.date | None = None
    focus: str = ""
    done: str = ""
    mood: str = ""
    energy: int | None = Field(default=None, ge=1, le=10)
    note: str = ""


class DailyCheckinOut(ORMModel):
    id: int
    date: datetime.date
    focus: str
    done: str
    mood: str
    energy: int | None = None
    note: str = ""
    ai_summary: dict | None = None
    status: str
    updated_at: datetime.datetime | None = None


class ScheduleBlockCreate(BaseModel):
    date: datetime.date
    title: str = Field(min_length=1, max_length=255)
    kind: str = "study"
    start_time: str | None = None    # "HH:MM"
    end_time: str | None = None      # "HH:MM"
    minutes: int = Field(default=60, ge=10, le=600)


class ScheduleBlockOut(ORMModel):
    id: int
    date: datetime.date
    start_time: str | None = None
    end_time: str | None = None
    title: str
    kind: str
    minutes: int
    source: str
    linked_type: str | None = None
    linked_id: str | None = None
    completed: bool
    order_index: int
    created_at: datetime.datetime | None = None