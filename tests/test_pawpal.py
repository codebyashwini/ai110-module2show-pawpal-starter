import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


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


class TestSortingCorrectness:
    """Tests for sort_tasks_by_time method."""

    def test_sort_tasks_chronological_order(self):
        """Verify that tasks are sorted by preferred_time_window in chronological order."""
        owner = Owner(name="Bob", available_hours_per_day=3)
        pet = Pet(name="Spot", species="Dog", owner=owner)

        # Create tasks OUT OF ORDER
        task_evening = Task(
            title="Evening walk",
            duration_minutes=30,
            priority="medium",
            preferred_time_window=("18:00", "19:00")
        )
        task_morning = Task(
            title="Morning walk",
            duration_minutes=45,
            priority="high",
            preferred_time_window=("07:00", "08:00")
        )
        task_afternoon = Task(
            title="Afternoon play",
            duration_minutes=20,
            priority="low",
            preferred_time_window=("15:00", "16:00")
        )

        pet.add_task(task_evening)
        pet.add_task(task_morning)
        pet.add_task(task_afternoon)

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_tasks_by_time(pet.tasks)

        # Verify order: morning (07:00), afternoon (15:00), evening (18:00)
        assert sorted_tasks[0].title == "Morning walk"
        assert sorted_tasks[1].title == "Afternoon play"
        assert sorted_tasks[2].title == "Evening walk"

    def test_sort_tasks_without_time_window_appear_last(self):
        """Verify that tasks without preferred_time_window are sorted to the end."""
        owner = Owner(name="Charlie", available_hours_per_day=4)
        pet = Pet(name="Whiskers", species="Cat", owner=owner)

        task_with_time = Task(
            title="Feeding at noon",
            duration_minutes=15,
            priority="high",
            preferred_time_window=("12:00", "13:00")
        )
        task_without_time = Task(
            title="Flexible grooming",
            duration_minutes=45,
            priority="medium"
            # No preferred_time_window
        )

        pet.add_task(task_without_time)
        pet.add_task(task_with_time)

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_tasks_by_time(pet.tasks)

        # Task with time should come first
        assert sorted_tasks[0].preferred_time_window is not None
        assert sorted_tasks[0].title == "Feeding at noon"
        # Task without time should come last
        assert sorted_tasks[1].preferred_time_window is None
        assert sorted_tasks[1].title == "Flexible grooming"

    def test_sort_empty_task_list(self):
        """Verify that sorting an empty list returns an empty list."""
        owner = Owner(name="Dave", available_hours_per_day=2)
        scheduler = Scheduler(owner)

        sorted_tasks = scheduler.sort_tasks_by_time([])

        assert sorted_tasks == []


class TestRecurrenceLogic:
    """Tests for recurring task creation via mark_task_complete."""

    def test_daily_task_creates_next_occurrence(self):
        """Verify that marking a daily task complete creates a new task for tomorrow."""
        owner = Owner(name="Eve", available_hours_per_day=3)
        pet = Pet(name="Milo", species="Dog", owner=owner)

        today = date.today()
        daily_task = Task(
            title="Daily walk",
            duration_minutes=30,
            priority="high",
            recurring="daily",
            due_date=today
        )
        pet.add_task(daily_task)

        # Before marking complete, pet should have 1 task
        assert len(pet.tasks) == 1

        scheduler = Scheduler(owner, pet=pet)
        next_task = scheduler.mark_task_complete(daily_task)

        # After marking complete:
        # 1. Original task should be marked completed
        assert daily_task.completed is True
        # 2. Next task should be created
        assert next_task is not None
        # 3. Next task should be for tomorrow
        tomorrow = today + timedelta(days=1)
        assert next_task.due_date == tomorrow
        # 4. Pet should now have 2 tasks (original + new)
        assert len(pet.tasks) == 2
        # 5. New task should have same properties
        assert next_task.title == daily_task.title
        assert next_task.duration_minutes == daily_task.duration_minutes
        assert next_task.recurring == "daily"

    def test_weekly_task_creates_next_occurrence(self):
        """Verify that marking a weekly task complete creates a new task for next week."""
        owner = Owner(name="Frank", available_hours_per_day=2)
        pet = Pet(name="Luna", species="Cat", owner=owner)

        today = date.today()
        weekly_task = Task(
            title="Weekly bath",
            duration_minutes=60,
            priority="medium",
            recurring="weekly",
            due_date=today
        )
        pet.add_task(weekly_task)

        scheduler = Scheduler(owner, pet=pet)
        next_task = scheduler.mark_task_complete(weekly_task)

        # Next task should be for next week (7 days later)
        next_week = today + timedelta(weeks=1)
        assert next_task.due_date == next_week
        assert next_task.recurring == "weekly"
        assert len(pet.tasks) == 2

    def test_one_time_task_does_not_create_next_occurrence(self):
        """Verify that marking a one-time task complete does NOT create a new task."""
        owner = Owner(name="Grace", available_hours_per_day=3)
        pet = Pet(name="Max", species="Dog", owner=owner)

        one_time_task = Task(
            title="Vet appointment",
            duration_minutes=45,
            priority="high",
            recurring="one-time",
            due_date=date.today()
        )
        pet.add_task(one_time_task)

        assert len(pet.tasks) == 1

        scheduler = Scheduler(owner, pet=pet)
        next_task = scheduler.mark_task_complete(one_time_task)

        # One-time task should return None
        assert next_task is None
        # Pet should still have only 1 task
        assert len(pet.tasks) == 1
        # Original task should be marked complete
        assert one_time_task.completed is True

    def test_recurring_task_without_due_date_does_not_create_next(self):
        """Verify that a recurring task without due_date doesn't create next occurrence."""
        owner = Owner(name="Hank", available_hours_per_day=2)
        pet = Pet(name="Buddy", species="Dog", owner=owner)

        recurring_no_date = Task(
            title="Flexible grooming",
            duration_minutes=30,
            priority="low",
            recurring="daily"
            # No due_date set
        )
        pet.add_task(recurring_no_date)

        scheduler = Scheduler(owner, pet=pet)
        next_task = scheduler.mark_task_complete(recurring_no_date)

        # Should return None because no due_date
        assert next_task is None
        assert len(pet.tasks) == 1


class TestConflictDetection:
    """Tests for detect_time_conflicts method."""

    def test_detect_overlapping_time_windows(self):
        """Verify that overlapping time windows are flagged as conflicts."""
        owner = Owner(name="Ivy", available_hours_per_day=4)
        pet1 = Pet(name="Daisy", species="Dog", owner=owner)
        pet2 = Pet(name="Smokey", species="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        # Task 1: 15:00-16:00
        task1 = Task(
            title="Dog training",
            duration_minutes=60,
            priority="high",
            preferred_time_window=("15:00", "16:00")
        )
        # Task 2: 15:30-16:30 (overlaps with task1)
        task2 = Task(
            title="Cat grooming",
            duration_minutes=60,
            priority="high",
            preferred_time_window=("15:30", "16:30")
        )

        pet1.add_task(task1)
        pet2.add_task(task2)
        all_tasks = owner.get_all_tasks()

        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_time_conflicts(all_tasks)

        # Should detect exactly 1 conflict
        assert len(conflicts) > 0
        assert "TIME CONFLICT" in conflicts[0]
        assert "Dog training" in conflicts[0]
        assert "Cat grooming" in conflicts[0]

    def test_no_conflict_non_overlapping_windows(self):
        """Verify that non-overlapping time windows do NOT trigger conflicts."""
        owner = Owner(name="Jack", available_hours_per_day=5)
        pet1 = Pet(name="Rex", species="Dog", owner=owner)
        pet2 = Pet(name="Mittens", species="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        # Task 1: 08:00-09:00
        task1 = Task(
            title="Morning walk",
            duration_minutes=60,
            priority="high",
            preferred_time_window=("08:00", "09:00")
        )
        # Task 2: 10:00-11:00 (no overlap)
        task2 = Task(
            title="Afternoon play",
            duration_minutes=60,
            priority="low",
            preferred_time_window=("10:00", "11:00")
        )

        pet1.add_task(task1)
        pet2.add_task(task2)
        all_tasks = owner.get_all_tasks()

        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_time_conflicts(all_tasks)

        # Should detect NO conflicts
        assert len(conflicts) == 0

    def test_no_conflict_when_task_lacks_time_window(self):
        """Verify that tasks without preferred_time_window don't create conflicts."""
        owner = Owner(name="Karen", available_hours_per_day=3)
        pet = Pet(name="Fido", species="Dog", owner=owner)
        owner.add_pet(pet)

        # Task 1: 14:00-15:00
        task1 = Task(
            title="Scheduled feeding",
            duration_minutes=60,
            priority="high",
            preferred_time_window=("14:00", "15:00")
        )
        # Task 2: No time window
        task2 = Task(
            title="Flexible playtime",
            duration_minutes=30,
            priority="medium"
            # No preferred_time_window
        )

        pet.add_task(task1)
        pet.add_task(task2)
        all_tasks = owner.get_all_tasks()

        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_time_conflicts(all_tasks)

        # Should detect NO conflicts (one has no window)
        assert len(conflicts) == 0

    def test_conflict_at_exact_boundary(self):
        """Verify that touching boundaries (end of one = start of next) don't conflict."""
        owner = Owner(name="Leo", available_hours_per_day=4)
        pet1 = Pet(name="Buddy", species="Dog", owner=owner)
        pet2 = Pet(name="Shadow", species="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        # Task 1: 09:00-10:00
        task1 = Task(
            title="Morning walk",
            duration_minutes=60,
            priority="high",
            preferred_time_window=("09:00", "10:00")
        )
        # Task 2: 10:00-11:00 (starts exactly when task1 ends)
        task2 = Task(
            title="Cat feeding",
            duration_minutes=60,
            priority="high",
            preferred_time_window=("10:00", "11:00")
        )

        pet1.add_task(task1)
        pet2.add_task(task2)
        all_tasks = owner.get_all_tasks()

        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_time_conflicts(all_tasks)

        # Touching boundaries should NOT conflict (using < in comparison)
        assert len(conflicts) == 0
