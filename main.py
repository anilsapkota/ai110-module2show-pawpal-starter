from datetime import time

from pawpal_system import (
    CareTask,
    Category,
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
milo = Pet(name="Milo", species="Dog", age=3)

milo.add_task(CareTask(
    title="Morning Walk",
    duration_minutes=30,
    priority=Priority.HIGH,
    category=Category.EXERCISE,
    preferred_time=TimeOfDay.MORNING,
))
milo.add_task(CareTask(
    title="Breakfast",
    duration_minutes=10,
    priority=Priority.HIGH,
    category=Category.FEEDING,
    preferred_time=TimeOfDay.MORNING,
))
milo.add_task(CareTask(
    title="Heartworm Pill",
    duration_minutes=5,
    priority=Priority.HIGH,
    category=Category.MEDICATION,
    preferred_time=TimeOfDay.MORNING,
    notes="Give with food",
))
milo.add_task(CareTask(
    title="Brush Coat",
    duration_minutes=20,
    priority=Priority.LOW,
    category=Category.GROOMING,
    preferred_time=TimeOfDay.EVENING,
))

# --- Pet 2: Luna the cat ---
luna = Pet(name="Luna", species="Cat", age=5)

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
luna.add_task(CareTask(
    title="Litter Box Clean",
    duration_minutes=10,
    priority=Priority.MEDIUM,
    category=Category.GROOMING,
    preferred_time=TimeOfDay.ANY,
))

owner.add_pet(milo)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Generate and print schedules
# ---------------------------------------------------------------------------

scheduler = Scheduler()
day_start = time(8, 0)  # 8:00 AM

print("=" * 50)
print("        TODAY'S SCHEDULE")
print("=" * 50)

for pet in owner.pets:
    schedule = scheduler.generate_schedule(owner, pet, day_start)
    print(f"\n--- {pet.name} ({pet.species}) ---")
    print(schedule.get_summary())

print("\n" + "=" * 50)
