import pytest
from pawpal_system import Owner, Pet, Task


class TestTaskCompletion:
    """Tests for Task completion functionality."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() changes the task's status from False to True."""
        task = Task(
            title="Feed the dog",
            duration_minutes=15,
            priority="high"
        )

        # Initially, task should not be completed
        assert task.completed is False

        # Mark the task as complete
        task.mark_complete()

        # Now it should be marked as completed
        assert task.completed is True


class TestTaskAddition:
    """Tests for adding tasks to pets."""

    def test_adding_task_increases_pet_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Create an owner and pet
        owner = Owner(name="Alice", available_hours_per_day=2)
        pet = Pet(name="Mochi", species="golden retriever", owner=owner)

        # Initially, pet should have no tasks
        assert len(pet.tasks) == 0

        # Add a task to the pet
        task1 = Task(
            title="Morning walk",
            duration_minutes=30,
            priority="high"
        )
        pet.add_task(task1)

        # Pet should now have 1 task
        assert len(pet.tasks) == 1

        # Add another task
        task2 = Task(
            title="Feeding",
            duration_minutes=15,
            priority="medium"
        )
        pet.add_task(task2)

        # Pet should now have 2 tasks
        assert len(pet.tasks) == 2

        # Verify the tasks are correctly stored
        assert pet.tasks[0].title == "Morning walk"
        assert pet.tasks[1].title == "Feeding"
