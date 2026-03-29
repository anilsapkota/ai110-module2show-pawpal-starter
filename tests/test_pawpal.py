import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import CareTask, Category, Pet, Priority, TimeOfDay


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

    assert task.is_complete is True, "Task should be complete after mark_complete()"


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
