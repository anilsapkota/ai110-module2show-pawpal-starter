import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, time, timedelta
from pawpal_system import (
    CareTask, Category, DailySchedule, Frequency, Owner,
    Pet, Priority, ScheduledTask, Scheduler, TimeOfDay,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(title: str = "Walk") -> CareTask:
    return CareTask(
        title=title,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        category=Category.EXERCISE,
    )


# ---------------------------------------------------------------------------
# Test 1: Task Completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should flip is_complete from False to True."""
    task = make_task("Morning Walk")

    assert task.is_complete is False, "Task should start incomplete"

    task.mark_complete()

    assert task.is_complete is True, (
        "Task should be complete after mark_complete()"
    )


# ---------------------------------------------------------------------------
# Test 2: Task Addition
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """add_task() should increase the pet's task count by one each call."""
    pet = Pet(name="Milo", species="Dog", age=3)

    assert len(pet.get_tasks()) == 0, "Pet should start with no tasks"

    pet.add_task(make_task("Breakfast"))
    assert len(pet.get_tasks()) == 1, "Pet should have 1 task after first add"

    pet.add_task(make_task("Evening Walk"))
    assert len(pet.get_tasks()) == 2, "Pet should have 2 tasks after second add"


# ---------------------------------------------------------------------------
# Test 3: Sorting Correctness — chronological order
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """sort_by_time() must return MORNING < AFTERNOON < EVENING < ANY."""
    scheduler = Scheduler()

    evening = CareTask(
        "Evening Walk", 30, Priority.MEDIUM, Category.EXERCISE,
        preferred_time=TimeOfDay.EVENING,
    )
    morning = CareTask(
        "Morning Feed", 15, Priority.MEDIUM, Category.FEEDING,
        preferred_time=TimeOfDay.MORNING,
    )
    any_time = CareTask(
        "Grooming", 20, Priority.MEDIUM, Category.GROOMING,
        preferred_time=TimeOfDay.ANY,
    )
    afternoon = CareTask(
        "Afternoon Play", 25, Priority.MEDIUM, Category.ENRICHMENT,
        preferred_time=TimeOfDay.AFTERNOON,
    )

    result = scheduler.sort_by_time([evening, morning, any_time, afternoon])
    order = [t.preferred_time for t in result]

    assert order == [
        TimeOfDay.MORNING,
        TimeOfDay.AFTERNOON,
        TimeOfDay.EVENING,
        TimeOfDay.ANY,
    ], f"Expected MORNING→AFTERNOON→EVENING→ANY, got {order}"


def test_sort_by_priority_high_before_low():
    """sort_by_priority() must place HIGH tasks before MEDIUM and LOW."""
    scheduler = Scheduler()

    low = CareTask("Grooming", 20, Priority.LOW, Category.GROOMING)
    high = CareTask("Medication", 10, Priority.HIGH, Category.MEDICATION)
    medium = CareTask("Walk", 30, Priority.MEDIUM, Category.EXERCISE)

    result = scheduler.sort_by_priority([low, high, medium])

    assert result[0].priority == Priority.HIGH
    assert result[1].priority == Priority.MEDIUM
    assert result[2].priority == Priority.LOW


def test_sort_by_priority_tiebreak_by_time():
    """Within the same priority tier, MORNING tasks must come before EVENING ones."""
    scheduler = Scheduler()

    high_evening = CareTask(
        "Night Meds", 10, Priority.HIGH, Category.MEDICATION,
        preferred_time=TimeOfDay.EVENING,
    )
    high_morning = CareTask(
        "Morning Meds", 10, Priority.HIGH, Category.MEDICATION,
        preferred_time=TimeOfDay.MORNING,
    )

    result = scheduler.sort_by_priority([high_evening, high_morning])

    assert result[0].title == "Morning Meds", (
        "MORNING task should beat EVENING task at the same priority"
    )


# ---------------------------------------------------------------------------
# Test 4: Recurrence Logic — daily task spawns next occurrence
# ---------------------------------------------------------------------------

def test_mark_task_complete_daily_creates_next_day_task():
    """Completing a DAILY task must add a new task due the following day."""
    today = date.today()
    task = CareTask(
        title="Daily Feed",
        duration_minutes=10,
        priority=Priority.HIGH,
        category=Category.FEEDING,
        frequency=Frequency.DAILY,
        due_date=today,
    )
    pet = Pet(name="Luna", species="Cat")
    pet.add_task(task)

    scheduler = Scheduler()
    next_task = scheduler.mark_task_complete(pet, "Daily Feed")

    assert next_task is not None, (
        "DAILY task should produce a next occurrence"
    )
    tomorrow = today + timedelta(days=1)
    assert next_task.due_date == tomorrow, (
        f"Next occurrence should be due {tomorrow}, got {next_task.due_date}"
    )
    assert len(pet.get_tasks()) == 2, (
        "Pet should now have the original + new task"
    )


def test_mark_task_complete_weekly_creates_next_week_task():
    """Completing a WEEKLY task must add a new task due 7 days later."""
    today = date.today()
    task = CareTask(
        title="Weekly Bath",
        duration_minutes=30,
        priority=Priority.MEDIUM,
        category=Category.GROOMING,
        frequency=Frequency.WEEKLY,
        due_date=today,
    )
    pet = Pet(name="Rex", species="Dog")
    pet.add_task(task)

    scheduler = Scheduler()
    next_task = scheduler.mark_task_complete(pet, "Weekly Bath")

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_mark_task_complete_none_frequency_no_next_task():
    """Completing a one-off (Frequency.NONE) task must NOT create a follow-up."""
    task = CareTask(
        title="One-off Vet Visit",
        duration_minutes=60,
        priority=Priority.HIGH,
        category=Category.MEDICATION,
        frequency=Frequency.NONE,
    )
    pet = Pet(name="Bella", species="Dog")
    pet.add_task(task)

    scheduler = Scheduler()
    next_task = scheduler.mark_task_complete(pet, "One-off Vet Visit")

    assert next_task is None, (
        "Frequency.NONE task should never produce a next occurrence"
    )
    assert len(pet.get_tasks()) == 1, "Pet task list should not grow"


# ---------------------------------------------------------------------------
# Test 5: Conflict Detection — overlapping scheduled tasks
# ---------------------------------------------------------------------------

def test_detect_conflicts_exact_same_start_time():
    """Two tasks starting at the exact same time must be flagged as a conflict."""
    scheduler = Scheduler()

    task_a = CareTask("Feed", 30, Priority.HIGH, Category.FEEDING)
    task_b = CareTask("Walk", 20, Priority.MEDIUM, Category.EXERCISE)

    st_a = ScheduledTask(task_a, time(8, 0), time(8, 30))
    st_b = ScheduledTask(task_b, time(8, 0), time(8, 20))

    conflicts = scheduler.detect_conflicts([st_a, st_b])

    assert len(conflicts) == 1, (
        "Exact same start time should produce one conflict pair"
    )
    assert (st_a, st_b) in conflicts


def test_detect_conflicts_partial_overlap():
    """A task that starts before another ends must be flagged as a conflict."""
    scheduler = Scheduler()

    task_a = CareTask("Feed", 30, Priority.HIGH, Category.FEEDING)
    task_b = CareTask("Walk", 30, Priority.MEDIUM, Category.EXERCISE)

    # A runs 08:00–08:30, B starts at 08:15 (overlaps by 15 min)
    st_a = ScheduledTask(task_a, time(8, 0), time(8, 30))
    st_b = ScheduledTask(task_b, time(8, 15), time(8, 45))

    conflicts = scheduler.detect_conflicts([st_a, st_b])

    assert len(conflicts) == 1


def test_detect_conflicts_back_to_back_no_conflict():
    """Tasks that share a boundary (A ends exactly when B starts) must NOT conflict."""
    scheduler = Scheduler()

    task_a = CareTask("Feed", 30, Priority.HIGH, Category.FEEDING)
    task_b = CareTask("Walk", 20, Priority.MEDIUM, Category.EXERCISE)

    # A ends at 08:30, B starts at 08:30 — touching but not overlapping
    st_a = ScheduledTask(task_a, time(8, 0), time(8, 30))
    st_b = ScheduledTask(task_b, time(8, 30), time(8, 50))

    conflicts = scheduler.detect_conflicts([st_a, st_b])

    assert conflicts == [], (
        "Back-to-back tasks sharing only a boundary should not conflict"
    )


def test_conflict_warnings_returns_human_readable_strings():
    """conflict_warnings() must return strings describing overlapping tasks."""
    scheduler = Scheduler()

    task_a = CareTask("Feed", 30, Priority.HIGH, Category.FEEDING)
    task_b = CareTask("Walk", 20, Priority.MEDIUM, Category.EXERCISE)

    st_a = ScheduledTask(task_a, time(8, 0), time(8, 30))
    st_b = ScheduledTask(task_b, time(8, 0), time(8, 20))

    schedule = DailySchedule(date.today())
    schedule.add_scheduled_task(st_a)
    schedule.add_scheduled_task(st_b)

    warnings = scheduler.conflict_warnings([("Milo", schedule)])

    assert len(warnings) == 1
    assert "Feed" in warnings[0]
    assert "Walk" in warnings[0]


def test_detect_conflicts_no_overlap_returns_empty():
    """Fully separated tasks must produce no conflicts."""
    scheduler = Scheduler()

    task_a = CareTask("Feed", 20, Priority.HIGH, Category.FEEDING)
    task_b = CareTask("Walk", 20, Priority.MEDIUM, Category.EXERCISE)

    st_a = ScheduledTask(task_a, time(8, 0), time(8, 20))
    st_b = ScheduledTask(task_b, time(9, 0), time(9, 20))

    assert scheduler.detect_conflicts([st_a, st_b]) == []


# ---------------------------------------------------------------------------
# Test 6: Edge Cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_generates_empty_schedule():
    """A pet with no tasks should produce a valid empty schedule."""
    owner = Owner("Alice", available_minutes_per_day=120)
    pet = Pet(name="Ghost", species="Cat")
    owner.add_pet(pet)

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner, pet, time(8, 0))

    assert schedule.scheduled_tasks == []
    assert schedule.skipped_tasks == []
    assert schedule.total_minutes_used == 0


def test_zero_budget_skips_all_tasks():
    """Owner with 0 available minutes must have every task skipped."""
    owner = Owner("Bob", available_minutes_per_day=0)
    pet = Pet(name="Max", species="Dog")
    pet.add_task(CareTask(
        "Feed", 10, Priority.HIGH, Category.FEEDING,
        is_daily=True, recurrence_days=list(range(7)),
    ))

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner, pet, time(8, 0))

    assert schedule.scheduled_tasks == []
    assert len(schedule.skipped_tasks) == 1


def test_remove_nonexistent_task_is_safe():
    """remove_task() with an unknown title must not raise or alter the list."""
    pet = Pet(name="Milo", species="Dog")
    pet.add_task(make_task("Walk"))

    pet.remove_task("Nonexistent Task")

    assert len(pet.get_tasks()) == 1
