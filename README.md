# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Scheduler` class was extended with four groups of algorithmic
improvements during Module 2.

### Sorting

- **`sort_by_priority(tasks)`** — ranks tasks HIGH -> MEDIUM -> LOW.
  Ties within a priority tier are broken by time of day
  (MORNING before AFTERNOON before EVENING), so the most important,
  time-sensitive work lands first in the day.
- **`sort_by_time(tasks)`** — orders any task list chronologically
  by `preferred_time`, useful for a human-readable daily view
  independent of priority.

### Filtering

- **`filter_due_tasks(tasks, for_date)`** — returns tasks due on a
  given date using each task's `recurrence_days` list (0=Mon…6=Sun),
  supporting tasks that recur on specific weekdays only.
- **`filter_tasks(tasks, ...)`** — composable filter by completion
  status, `Category`, and `TimeOfDay`; each active parameter
  narrows the result of the previous one.
- **`filter_by_pet_or_status(pets, ...)`** — searches across all
  pets and returns `(pet_name, task)` pairs, optionally scoped to
  one pet or to incomplete tasks only.

### Recurring Tasks

- `CareTask` now carries a `Frequency` (NONE / DAILY / WEEKLY)
  and a `due_date`.
- **`CareTask.next_occurrence()`** uses `timedelta` to compute the
  next due date: `timedelta(days=1)` for DAILY,
  `timedelta(weeks=1)` for WEEKLY, `None` for one-off tasks.
- **`Scheduler.mark_task_complete(pet, title)`** marks the task
  done and automatically appends its next occurrence to the pet's
  task list so tomorrow's schedule is always up to date.

### Conflict Detection

- **`detect_conflicts(scheduled_tasks)`** — low-level O(n²)
  pairwise check via `ScheduledTask.overlaps_with()`; returns
  raw conflict pairs.
- **`conflict_warnings(named_schedules)`** — never-crashing wrapper
  that accepts `(pet_name, DailySchedule)` pairs, checks for
  overlaps within and across pets, and returns plain-English
  warning strings (empty list = no conflicts).
- Warnings are auto-attached to every `DailySchedule` from
  `generate_schedule()` and printed by `get_summary()`.

### Budget Fitting

- **`fit_to_budget(tasks, available_minutes)`** — greedy packing
  with a within-tier duration sort (largest tasks first per
  priority tier) to reduce wasted slack vs. naive first-fit.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
