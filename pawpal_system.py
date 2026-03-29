from __future__ import annotations
from datetime import date, time
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Category(Enum):
    EXERCISE = "exercise"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"


class TimeOfDay(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANY = "any"


# ---------------------------------------------------------------------------
# CareTask
# ---------------------------------------------------------------------------

class CareTask:
    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: Priority,
        category: Category,
        preferred_time: TimeOfDay = TimeOfDay.ANY,
        notes: str = "",
        is_daily: bool = True,
    ) -> None:
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.preferred_time = preferred_time
        self.notes = notes
        self.is_daily = is_daily

    def is_high_priority(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        age: int = 0,
        notes: str = "",
    ) -> None:
        self.name = name
        self.species = species
        self.age = age
        self.notes = notes
        self.tasks: list[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def edit_task(self, title: str, updated_fields: dict) -> None:
        pass

    def get_tasks(self) -> list[CareTask]:
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        available_minutes_per_day: int,
        preferences: Optional[dict] = None,
    ) -> None:
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_name: str) -> None:
        pass

    def get_time_budget(self) -> int:
        pass


# ---------------------------------------------------------------------------
# ScheduledTask
# ---------------------------------------------------------------------------

class ScheduledTask:
    def __init__(
        self,
        task: CareTask,
        start_time: time,
        end_time: time,
    ) -> None:
        self.task = task
        self.start_time = start_time
        self.end_time = end_time

    def display(self) -> str:
        pass

    def overlaps_with(self, other: ScheduledTask) -> bool:
        pass


# ---------------------------------------------------------------------------
# DailySchedule
# ---------------------------------------------------------------------------

class DailySchedule:
    def __init__(self, schedule_date: date) -> None:
        self.date = schedule_date
        self.scheduled_tasks: list[ScheduledTask] = []
        self.skipped_tasks: list[CareTask] = []
        self.total_minutes_used: int = 0
        self.explanation: str = ""

    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        pass

    def add_skipped_task(self, task: CareTask) -> None:
        pass

    def get_summary(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def generate_schedule(
        self,
        owner: Owner,
        pet: Pet,
        day_start_time: time,
    ) -> DailySchedule:
        pass

    def sort_by_priority(self, tasks: list[CareTask]) -> list[CareTask]:
        pass

    def filter_due_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        pass

    def fit_to_budget(
        self,
        tasks: list[CareTask],
        available_minutes: int,
    ) -> list[CareTask]:
        pass

    def assign_times(
        self,
        tasks: list[CareTask],
        start_time: time,
    ) -> list[ScheduledTask]:
        pass

    def generate_explanation(self, schedule: DailySchedule) -> str:
        pass
