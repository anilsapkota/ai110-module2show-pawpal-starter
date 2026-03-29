# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Add/edit a pet profile — Enter basic info about their pet and themselves (name, pet type, available time per day, preferences).

Add and manage care tasks — Create tasks like walks, feeding, or medication with a duration and priority level, and edit or remove them as needed.

Generate and view today's schedule — Trigger the scheduler to produce a prioritized daily care plan and see the reasoning behind it (e.g., why high-priority tasks were placed first).




1. Owner
Attributes:

name: str
available_minutes_per_day: int — total daily time budget
preferences: dict — e.g., preferred start time, task type preferences
pets: list[Pet] — supports multiple pets
Methods:

add_pet(pet) — adds a pet to the owner's list
remove_pet(pet_name) — removes a pet by name
get_time_budget() — returns available_minutes_per_day
2. Pet
Attributes:

name: str
species: str — dog, cat, other
age: int (optional)
notes: str — special needs or health info
tasks: list[CareTask] — tasks belong to the pet, not the owner
Methods:

add_task(task) — adds a care task
remove_task(task_title) — removes a task by title
edit_task(task_title, updated_fields) — updates an existing task
get_tasks() — returns the full task list
3. CareTask
Attributes:

title: str — e.g., "Morning walk"
duration_minutes: int
priority: Priority — enum, not raw string
category: Category — enum (EXERCISE, FEEDING, etc.)
preferred_time: TimeOfDay — enum, used by the scheduler for ordering
Methods:

is_high_priority() — returns True if priority == Priority.HIGH
to_dict() — serializes for display or storage
4. ScheduledTask
A CareTask paired with its assigned time slot in the day.

Attributes:

task: CareTask
start_time: datetime.time — not a string; enables arithmetic
end_time: datetime.time — computed from start_time + duration_minutes
Methods:

display() — returns a formatted string, e.g., "8:00–8:20 AM | Morning walk (high)"
overlaps_with(other: ScheduledTask) — checks for time conflicts
5. DailySchedule
A pure data object — holds results only, contains no scheduling or AI logic.

Attributes:

date: datetime.date
scheduled_tasks: list[ScheduledTask] — ordered list of placed tasks
skipped_tasks: list[CareTask] — tasks that didn't fit the time budget
total_minutes_used: int
explanation: str — plain-text reasoning, written by Scheduler, stored here
Methods:

add_scheduled_task(scheduled_task) — appends to the schedule
get_summary() — returns a readable overview of the day's plan
6. Scheduler
A stateless service — takes inputs as parameters, returns a DailySchedule. Owns all scheduling and explanation logic.

Attributes: none (stateless)

Methods:

generate_schedule(owner, pet, tasks, day_start_time) → DailySchedule — main entry point
sort_by_priority(tasks) — orders tasks HIGH → MEDIUM → LOW, then by preferred_time
fit_to_budget(tasks, available_minutes) — selects tasks that fit within the time budget, populates skipped_tasks
assign_times(tasks, start_time) — converts ordered tasks into ScheduledTask objects with real clock times
generate_explanation(schedule) → str — produces natural language reasoning (can call Claude API here); result is stored in DailySchedule.explanation
Relationship Map

Owner ──── has ───► list[Pet]
Pet   ──── has ───► list[CareTask]

Scheduler.generate_schedule(owner, pet, tasks, day_start_time)
    └──► returns DailySchedule
              ├── list[ScheduledTask]  (each wraps a CareTask + datetime.time)
              ├── list[CareTask]       (skipped)
              └── explanation: str
Key design principles applied:

Tasks live on Pet, not Owner
DailySchedule is a data object only — no logic
Scheduler is stateless — no stored owner/pet/task fields
All scheduling and explanation responsibility lives in Scheduler
preferred_time is actually used in sort_by_priority()
All times are datetime.time, not strings


Mermaid.js code :
classDiagram
    class Owner {
        +str name
        +int available_minutes_per_day
        +dict preferences
        +list~Pet~ pets
        +add_pet(pet)
        +remove_pet(pet_name)
        +get_time_budget() int
    }

    class Pet {
        +str name
        +str species
        +int age
        +str notes
        +list~CareTask~ tasks
        +add_task(task)
        +remove_task(title)
        +edit_task(title, updated_fields)
        +get_tasks() list
    }

    class CareTask {
        +str title
        +int duration_minutes
        +Priority priority
        +Category category
        +TimeOfDay preferred_time
        +str notes
        +bool is_daily
        +is_high_priority() bool
        +to_dict() dict
    }

    class ScheduledTask {
        +CareTask task
        +time start_time
        +time end_time
        +display() str
        +overlaps_with(other) bool
    }

    class DailySchedule {
        +date date
        +list~ScheduledTask~ scheduled_tasks
        +list~CareTask~ skipped_tasks
        +int total_minutes_used
        +str explanation
        +add_scheduled_task(scheduled_task)
        +add_skipped_task(task)
        +get_summary() str
    }

    class Scheduler {
        +generate_schedule(owner, pet, day_start_time) DailySchedule
        +sort_by_priority(tasks) list
        +filter_due_tasks(tasks) list
        +fit_to_budget(tasks, available_minutes) list
        +assign_times(tasks, start_time) list
        +generate_explanation(schedule) str
    }

    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
    }

    class Category {
        <<enumeration>>
        EXERCISE
        FEEDING
        MEDICATION
        GROOMING
        ENRICHMENT
    }

    class TimeOfDay {
        <<enumeration>>
        MORNING
        AFTERNOON
        EVENING
        ANY
    }

    Owner "1" *-- "0..*" Pet : has
    Pet "1" *-- "0..*" CareTask : has
    Scheduler --> Owner : uses
    Scheduler --> Pet : uses
    Scheduler --> DailySchedule : produces
    DailySchedule "1" *-- "0..*" ScheduledTask : contains
    DailySchedule "1" o-- "0..*" CareTask : skipped
    ScheduledTask --> CareTask : wraps
    CareTask --> Priority : uses
    CareTask --> Category : uses
    CareTask --> TimeOfDay : uses

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

yes i did several times. I asked gpt to respond to claude's response and fed that again to chatgpt to improve it as well. One change was how the owner could have several pets instead of just one pet

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

sort_by_time() + sort_by_priority() — two-key lambda sorts
filter_due_tasks(), filter_tasks(), filter_by_pet_or_status() — composable filters
fit_to_budget() — greedy packing with within-tier duration sort
mark_task_complete() — auto-generates next recurring occurrence
conflict_warnings() — warn-not-crash overlap detection across pets


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The "HH:MM-HH:MM" string was duplicated inside conflict_warnings(). Extracting it as a small helper on ScheduledTask follows the rule: data knows how to describe itself. display() now calls it too, so the format lives in exactly one place.

Flatten rewritten as a list comprehension 

Before	After
4 lines, for + for + .append()	4 lines, nested comprehension
Mutates labelled mid-build	Builds labelled in one expression
A list comprehension over a nested loop is both idiomatic Python and slightly faster — no repeated attribute lookups for .append, and the interpreter can pre-allocate the result list.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
