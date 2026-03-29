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
        st.table([t.to_dict() for t in tasks])
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
            schedule = Scheduler().generate_schedule(owner, sched_pet, day_start)

            st.success(
                f"Schedule ready — {schedule.total_minutes_used} of "
                f"{owner.available_minutes_per_day} min used."
            )

            if schedule.scheduled_tasks:
                st.markdown("#### Scheduled")
                for item in schedule.scheduled_tasks:
                    badge = "🔴" if item.task.is_high_priority() else "🟡"
                    st.markdown(
                        f"- {badge} **{item.display()}** — _{item.task.category.value}_"
                    )

            if schedule.skipped_tasks:
                st.markdown("#### Skipped (over budget)")
                for skipped in schedule.skipped_tasks:
                    st.markdown(f"- ~~{skipped.title}~~ ({skipped.duration_minutes} min)")

            if schedule.explanation:
                st.info(schedule.explanation)
