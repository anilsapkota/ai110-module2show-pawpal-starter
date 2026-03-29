from datetime import time

from pawpal_system import (
    CareTask,
    Category,
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    TimeOfDay,
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

owner = Owner(name="Alex", available_minutes_per_day=90)

# --- Pet 1: Milo the dog ---
# Tasks added intentionally OUT OF ORDER (evening -> afternoon -> morning)
milo = Pet(name="Milo", species="Dog", age=3)

milo.add_task(CareTask(
    title="Brush Coat",
    duration_minutes=20,
    priority=Priority.LOW,
    category=Category.GROOMING,
    preferred_time=TimeOfDay.EVENING,
))
milo.add_task(CareTask(
    title="Afternoon Walk",
    duration_minutes=25,
    priority=Priority.MEDIUM,
    category=Category.EXERCISE,
    preferred_time=TimeOfDay.AFTERNOON,
))
milo.add_task(CareTask(
    title="Heartworm Pill",
    duration_minutes=5,
    priority=Priority.HIGH,
    category=Category.MEDICATION,
    preferred_time=TimeOfDay.MORNING,
    notes="Give with food",
    frequency=Frequency.WEEKLY,   # vet-prescribed, once a week
))
milo.add_task(CareTask(
    title="Breakfast",
    duration_minutes=10,
    priority=Priority.HIGH,
    category=Category.FEEDING,
    preferred_time=TimeOfDay.MORNING,
    frequency=Frequency.DAILY,    # every morning
))
milo.add_task(CareTask(
    title="Morning Walk",
    duration_minutes=30,
    priority=Priority.HIGH,
    category=Category.EXERCISE,
    preferred_time=TimeOfDay.MORNING,
    frequency=Frequency.DAILY,    # every morning
))

# --- Pet 2: Luna the cat ---
# Also added out of order (evening -> morning -> afternoon)
luna = Pet(name="Luna", species="Cat", age=5)

luna.add_task(CareTask(
    title="Litter Box Clean",
    duration_minutes=10,
    priority=Priority.MEDIUM,
    category=Category.GROOMING,
    preferred_time=TimeOfDay.EVENING,
))
luna.add_task(CareTask(
    title="Wet Food",
    duration_minutes=5,
    priority=Priority.HIGH,
    category=Category.FEEDING,
    preferred_time=TimeOfDay.MORNING,
))
luna.add_task(CareTask(
    title="Laser Pointer Play",
    duration_minutes=15,
    priority=Priority.MEDIUM,
    category=Category.ENRICHMENT,
    preferred_time=TimeOfDay.AFTERNOON,
))

# Mark one task complete so filtering demo is visible
luna.tasks[0].mark_complete()  # Litter Box Clean is done

owner.add_pet(milo)
owner.add_pet(luna)

scheduler = Scheduler()
day_start = time(8, 0)  # 8:00 AM

# ---------------------------------------------------------------------------
# Demo 1 — sort_by_time(): tasks in chronological order per pet
# ---------------------------------------------------------------------------

print("=" * 50)
print("  DEMO 1: sort_by_time() — tasks added out of")
print("  order, now sorted MORNING -> AFTERNOON -> EVENING")
print("=" * 50)

for pet in owner.pets:
    print(f"\n--- {pet.name} ({pet.species}) ---")
    sorted_tasks = scheduler.sort_by_time(pet.get_tasks())
    for t in sorted_tasks:
        status = "[DONE]" if t.is_complete else "[ ]  "
        print(
            f"  {status} [{t.preferred_time.value:<10}] "
            f"{t.title} ({t.duration_minutes} min)"
        )

# ---------------------------------------------------------------------------
# Demo 2 — filter_by_pet_or_status(): narrow by pet name or completion
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("  DEMO 2: filter_by_pet_or_status()")
print("=" * 50)

all_pets = owner.pets

# 2a — all incomplete tasks across every pet
incomplete = scheduler.filter_by_pet_or_status(
    all_pets, only_incomplete=True
)
print("\n  Incomplete tasks (all pets):")
for pet_name, task in incomplete:
    print(f"    [{pet_name}] {task.title}")

# 2b — all tasks for Milo only
milo_tasks = scheduler.filter_by_pet_or_status(
    all_pets, pet_name="Milo"
)
print("\n  All tasks for Milo:")
for pet_name, task in milo_tasks:
    status = "DONE" if task.is_complete else "todo"
    print(f"    ({status}) {task.title}")

# 2c — incomplete tasks for Luna only
luna_incomplete = scheduler.filter_by_pet_or_status(
    all_pets, pet_name="Luna", only_incomplete=True
)
print("\n  Incomplete tasks for Luna:")
for pet_name, task in luna_incomplete:
    print(f"    {task.title}")

# ---------------------------------------------------------------------------
# Demo 3 — full schedule generation (unchanged pipeline)
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("  DEMO 3: generated schedules")
print("=" * 50)

for pet in owner.pets:
    schedule = scheduler.generate_schedule(owner, pet, day_start)
    print(f"\n--- {pet.name} ({pet.species}) ---")
    print(schedule.get_summary())

# ---------------------------------------------------------------------------
# Demo 4 — mark_task_complete(): auto-creates next occurrence via timedelta
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("  DEMO 4: mark_task_complete() recurring tasks")
print("=" * 50)

demo_cases = [
    (milo, "Morning Walk"),      # DAILY  -> due tomorrow
    (milo, "Heartworm Pill"),    # WEEKLY -> due in 7 days
    (milo, "Brush Coat"),        # NONE   -> one-off, no next occurrence
]

for pet, title in demo_cases:
    next_task = scheduler.mark_task_complete(pet, title)
    # Find the now-completed original to show its due_date
    original = next(t for t in pet.tasks if t.title == title)
    print(f"\n  Completed: '{title}' (due {original.due_date})")
    if next_task:
        print(
            f"  Next occurrence ({next_task.frequency.value}): "
            f"'{next_task.title}' due {next_task.due_date}"
        )
    else:
        print("  One-off task -- no next occurrence created.")

print()

# Show Milo's updated task list so new occurrences are visible
print("  Milo's tasks after completions:")
for t in milo.get_tasks():
    status = "[DONE]" if t.is_complete else "[ ]  "
    print(
        f"    {status} {t.title} "
        f"(due {t.due_date}, {t.frequency.value})"
    )

print("\n" + "=" * 50)
