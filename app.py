import streamlit as st
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

_scheduler = Scheduler()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner.")

# ---------------------------------------------------------------------------
# Step 2: Session state "vault" — Owner lives here across reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Owner Setup
# ---------------------------------------------------------------------------

st.header("Owner")

if st.session_state.owner is None:
    with st.form("owner_form"):
        col1, col2 = st.columns(2)
        with col1:
            o_name = st.text_input("Your name", value="Jordan")
        with col2:
            o_budget = st.number_input(
                "Available minutes per day", min_value=10, max_value=480, value=90
            )
        if st.form_submit_button("Create profile"):
            st.session_state.owner = Owner(
                name=o_name, available_minutes_per_day=int(o_budget)
            )
            st.rerun()
else:
    owner: Owner = st.session_state.owner
    st.success(f"**{owner.name}** — {owner.available_minutes_per_day} min/day available")
    if st.button("Reset owner"):
        st.session_state.owner = None
        st.rerun()

# Don't render the rest until an Owner exists
if st.session_state.owner is None:
    st.stop()

owner: Owner = st.session_state.owner

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Pets — owner.add_pet() wired to form submit
# ---------------------------------------------------------------------------

st.header("Pets")

col_list, col_form = st.columns([2, 1])

with col_form:
    with st.expander("Add a pet", expanded=len(owner.pets) == 0):
        with st.form("add_pet_form"):
            p_name = st.text_input("Pet name", value="Mochi")
            p_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
            p_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
            p_notes = st.text_input("Notes (optional)", value="")
            if st.form_submit_button("Add pet"):
                owner.add_pet(
                    Pet(name=p_name, species=p_species, age=int(p_age), notes=p_notes)
                )
                st.rerun()

with col_list:
    if not owner.pets:
        st.info("No pets yet. Add one using the form →")
    else:
        for pet in owner.pets:
            count = len(pet.get_tasks())
            st.markdown(
                f"**{pet.name}** ({pet.species}, age {pet.age}) — {count} task(s)"
            )

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Tasks — pet.add_task() wired to form submit
# ---------------------------------------------------------------------------

st.header("Tasks")

if not owner.pets:
    st.info("Add a pet first before managing tasks.")
else:
    PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
    CATEGORY_MAP = {c.value: c for c in Category}
    TIME_MAP = {t.value: t for t in TimeOfDay}

    selected_pet_name = st.selectbox(
        "Manage tasks for", [p.name for p in owner.pets], key="task_pet"
    )
    selected_pet: Pet = next(p for p in owner.pets if p.name == selected_pet_name)

    with st.expander("Add a task", expanded=True):
        with st.form("add_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                t_title = st.text_input("Task title", value="Morning walk")
                t_duration = st.number_input(
                    "Duration (minutes)", min_value=1, max_value=240, value=20
                )
                t_priority = st.selectbox("Priority", list(PRIORITY_MAP), index=2)
            with col2:
                t_category = st.selectbox("Category", list(CATEGORY_MAP))
                t_time = st.selectbox("Preferred time", list(TIME_MAP))
                t_notes = st.text_input("Notes (optional)", value="")
            t_daily = st.checkbox("Daily task", value=True)

            if st.form_submit_button("Add task"):
                selected_pet.add_task(
                    CareTask(
                        title=t_title,
                        duration_minutes=int(t_duration),
                        priority=PRIORITY_MAP[t_priority],
                        category=CATEGORY_MAP[t_category],
                        preferred_time=TIME_MAP[t_time],
                        notes=t_notes,
                        is_daily=t_daily,
                    )
                )
                st.rerun()

    tasks = selected_pet.get_tasks()
    if tasks:
        st.markdown(f"**{selected_pet.name}'s tasks:**")

        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            sort_by = st.selectbox(
                "Sort by",
                ["Priority", "Time of day"],
                key="task_sort",
            )
        with fcol2:
            filter_cat = st.selectbox(
                "Filter by category",
                ["All"] + [c.value for c in Category],
                key="task_filter_cat",
            )
        with fcol3:
            filter_time = st.selectbox(
                "Filter by time",
                ["All"] + [t.value for t in TimeOfDay if t != TimeOfDay.ANY],
                key="task_filter_time",
            )

        # Apply Scheduler filtering
        cat_arg = CATEGORY_MAP.get(filter_cat)
        time_arg = TIME_MAP.get(filter_time)
        filtered = _scheduler.filter_tasks(
            tasks,
            only_incomplete=False,
            category=cat_arg,
            time_of_day=time_arg,
        )

        # Apply Scheduler sorting
        if sort_by == "Priority":
            display_tasks = _scheduler.sort_by_priority(filtered)
        else:
            display_tasks = _scheduler.sort_by_time(filtered)

        if not display_tasks:
            st.info("No tasks match the current filters.")
        else:
            PRIORITY_ICON = {
                Priority.HIGH: "🔴",
                Priority.MEDIUM: "🟡",
                Priority.LOW: "🟢",
            }
            rows = []
            for t in display_tasks:
                rows.append({
                    "": PRIORITY_ICON[t.priority],
                    "Title": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Category": t.category.value,
                    "Time": t.preferred_time.value,
                    "Priority": t.priority.value,
                    "Daily": "Yes" if t.is_daily else "No",
                    "Done": "✔" if t.is_complete else "",
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(f"No tasks yet for {selected_pet.name}.")

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule — Scheduler.generate_schedule() wired to button
# ---------------------------------------------------------------------------

st.header("Generate Schedule")

if not owner.pets:
    st.info("Add a pet with tasks before generating a schedule.")
else:
    sched_pet_name = st.selectbox(
        "Schedule for which pet?", [p.name for p in owner.pets], key="sched_pet"
    )
    sched_pet: Pet = next(p for p in owner.pets if p.name == sched_pet_name)
    day_start = st.time_input("Day starts at", value=time(8, 0))

    if st.button("Generate schedule", type="primary"):
        if not sched_pet.get_tasks():
            st.warning(f"{sched_pet.name} has no tasks to schedule.")
        else:
            schedule = _scheduler.generate_schedule(owner, sched_pet, day_start)

            # ── Conflict warnings — shown first so they're impossible to miss ──
            if schedule.warnings:
                n = len(schedule.warnings)
                st.error(
                    f"⚠️ **{n} scheduling conflict(s) detected "
                    f"for {sched_pet.name}!** "
                    "Two tasks overlap — review or adjust durations."
                )
                for w in schedule.warnings:
                    st.warning(f"🔔 {w}")

            # ── Budget summary ──
            used = schedule.total_minutes_used
            budget = owner.available_minutes_per_day
            budget_pct = used / budget
            if budget_pct >= 1.0:
                st.warning(
                    f"Schedule uses **{used} of {budget} min**"
                    " — at full capacity."
                )
            else:
                st.success(
                    f"Schedule ready — **{used} of {budget} min** used "
                    f"({int(budget_pct * 100)}%)."
                )

            # ── Scheduled tasks table ──
            if schedule.scheduled_tasks:
                st.markdown("#### Scheduled")
                rows = []
                for item in schedule.scheduled_tasks:
                    priority_icon = "🔴" if item.task.is_high_priority() else (
                        "🟡" if item.task.priority.value == "medium" else "🟢"
                    )
                    rows.append({
                        "": priority_icon,
                        "Time slot": item.time_window(),
                        "Task": item.task.title,
                        "Duration": f"{item.task.duration_minutes} min",
                        "Category": item.task.category.value,
                        "Priority": item.task.priority.value,
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)

            # ── Skipped tasks ──
            if schedule.skipped_tasks:
                st.markdown("#### Skipped (over time budget)")
                for skipped in schedule.skipped_tasks:
                    st.warning(
                        f"⏭️ **{skipped.title}** "
                        f"({skipped.duration_minutes} min, "
                        f"{skipped.priority.value} priority)"
                        " — didn't fit in today's budget."
                    )

            if schedule.explanation:
                st.info(f"ℹ️ {schedule.explanation}")
