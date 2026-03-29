from __future__ import annotations
from datetime import date, datetime, time, timedelta
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
        self.is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is HIGH."""
        return self.priority == Priority.HIGH

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary with enum values as strings."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.value,
            "category": self.category.value,
            "preferred_time": self.preferred_time.value,
            "notes": self.notes,
            "is_daily": self.is_daily,
        }


# ---------------------------------------------------------------------------
# Pet class 

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
        """Append a CareTask to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the task matching the given title; silently does nothing if not found."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def edit_task(self, title: str, updated_fields: dict) -> None:
        """Update fields on the first task whose title matches; silently does nothing if not found."""
        for task in self.tasks:
            if task.title == title:
                for field, value in updated_fields.items():
                    setattr(task, field, value)
                return

    def get_tasks(self) -> list[CareTask]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)


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
        """Add a Pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet matching the given name from the roster."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_time_budget(self) -> int:
        """Return the owner's total available minutes per day."""
        return self.available_minutes_per_day


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
        """Return a formatted HH:MM–HH:MM label with the task title and duration."""
        return (
            f"{self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')} "
            f"{self.task.title} ({self.task.duration_minutes} min)"
        )

    def overlaps_with(self, other: ScheduledTask) -> bool:
        """Return True if this task's time window intersects with another's."""
        return self.start_time < other.end_time and other.start_time < self.end_time


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
        """Append a ScheduledTask and accumulate its duration into total_minutes_used."""
        self.scheduled_tasks.append(scheduled_task)
        self.total_minutes_used += scheduled_task.task.duration_minutes

    def add_skipped_task(self, task: CareTask) -> None:
        """Record a CareTask that could not be scheduled due to budget constraints."""
        self.skipped_tasks.append(task)

    def get_summary(self) -> str:
        """Return a human-readable multi-line summary of the day's schedule."""
        lines = [f"Schedule for {self.date} — {self.total_minutes_used} min used"]
        for st in self.scheduled_tasks:
            lines.append(f"  {st.display()}")
        if self.skipped_tasks:
            skipped = ", ".join(t.title for t in self.skipped_tasks)
            lines.append(f"  Skipped: {skipped}")
        if self.explanation:
            lines.append(f"  Note: {self.explanation}")
        return "\n".join(lines)


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
        """Run the full scheduling pipeline and return a populated DailySchedule."""
        schedule = DailySchedule(date.today())

        due = self.filter_due_tasks(pet.get_tasks())
        sorted_tasks = self.sort_by_priority(due)
        fitting = self.fit_to_budget(sorted_tasks, owner.get_time_budget())

        scheduled = self.assign_times(fitting, day_start_time)
        for st in scheduled:
            schedule.add_scheduled_task(st)

        scheduled_titles = {st.task.title for st in scheduled}
        for task in due:
            if task.title not in scheduled_titles:
                schedule.add_skipped_task(task)

        schedule.explanation = self.generate_explanation(schedule)
        return schedule

    def sort_by_priority(self, tasks: list[CareTask]) -> list[CareTask]:
        """Return tasks sorted HIGH → MEDIUM → LOW priority."""
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: priority_order[t.priority])

    def filter_due_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        """Return only tasks marked as daily (is_daily=True)."""
        return [t for t in tasks if t.is_daily]

    def fit_to_budget(
        self,
        tasks: list[CareTask],
        available_minutes: int,
    ) -> list[CareTask]:
        """Greedily select tasks that fit within the available time budget."""
        result = []
        remaining = available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                result.append(task)
                remaining -= task.duration_minutes
        return result

    def assign_times(
        self,
        tasks: list[CareTask],
        start_time: time,
    ) -> list[ScheduledTask]:
        """Assign sequential start/end times to each task beginning at start_time."""
        scheduled = []
        current = datetime.combine(date.today(), start_time)
        for task in tasks:
            end = current + timedelta(minutes=task.duration_minutes)
            scheduled.append(ScheduledTask(task, current.time(), end.time()))
            current = end
        return scheduled

    def generate_explanation(self, schedule: DailySchedule) -> str:
        """Build a plain-English summary of what was scheduled and what was skipped."""
        n_scheduled = len(schedule.scheduled_tasks)
        n_skipped = len(schedule.skipped_tasks)
        parts = [
            f"{n_scheduled} task(s) scheduled "
            f"({schedule.total_minutes_used} min)."
        ]
        if n_skipped:
            skipped = ", ".join(t.title for t in schedule.skipped_tasks)
            parts.append(
                f"{n_skipped} task(s) skipped due to time budget: {skipped}."
            )
        return " ".join(parts)
