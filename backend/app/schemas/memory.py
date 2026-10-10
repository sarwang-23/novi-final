from pydantic import BaseModel


class MemoryEntryOut(BaseModel):
    grade: str | None = None
    milestone: bool = False
    profile: bool = False
    text: str


class MemoryYearOut(BaseModel):
    school_year: str
    entries: list[MemoryEntryOut]


class StudentMemoryOut(BaseModel):
    core_profile: str = ""
    total_facts: int = 0
    years: list[MemoryYearOut] = []