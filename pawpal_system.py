"""
PawPal+ Backend Logic Layer
Classes for managing pets, owners, tasks, and scheduling.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional


class Owner:
    """Represents the person caring for the pet."""

    def __init__(self, name: str, available_hours_per_day: int, preferences: Optional[Dict] = None):
        """Initialize an owner with their name, availability, and optional preferences."""
        self.name = name
        self.available_hours_per_day = available_hours_per_day
        self.preferences = preferences or {}
        self.pets: List['Pet'] = []

    def get_available_hours(self) -> int:
        """Returns available hours per day."""
        return self.available_hours_per_day

    def set_preferences(self, preferences: Dict) -> None:
        """Updates owner preferences."""
        self.preferences.update(preferences)

    def add_pet(self, pet: 'Pet') -> None:
        """Adds a pet to the owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List['Task']:
        """Returns all tasks from all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Pet:
    """Represents the animal being cared for."""
    name: str
    species: str
    owner: Owner
    tasks: List['Task'] = field(default_factory=list)

    def get_owner(self) -> Owner:
        """Returns the Owner object."""
        return self.owner

    def display_info(self) -> str:
        """Returns formatted pet info (e.g., 'Mochi (golden retriever)')."""
        return f"{self.name} ({self.species})"

    def add_task(self, task: 'Task') -> None:
        """Adds a task to the pet's task list."""
        task.pet = self
        self.tasks.append(task)


@dataclass
class Task:
    """Represents a single care activity."""
    title: str
    duration_minutes: int
    priority: str  # low, medium, high
    pet: Optional['Pet'] = None  # which pet this task is for
    recurring: str = "one-time"  # daily, weekly, one-time
    preferred_time_window: Optional[tuple] = None  # e.g., ("07:00", "09:00") for time-specific tasks
    completed: bool = False

    def get_duration(self) -> int:
        """Returns task duration in minutes."""
        return self.duration_minutes

    def get_priority(self) -> str:
        """Returns priority level."""
        return self.priority

    def mark_complete(self) -> None:
        """Marks the task as completed."""
        self.completed = True


class Scheduler:
    """The engine that produces daily plans."""

    def __init__(self, owner: Owner, pet: Optional[Pet] = None, tasks: Optional[List[Task]] = None):
        """Initialize a scheduler for an owner with optional pet and tasks."""
        self.owner = owner
        self.pet = pet
        self.tasks = tasks or []

    def generate_schedule(self, target_date: date, pet: Optional[Pet] = None) -> 'DailySchedule':
        """Returns a DailySchedule for the given date, owner, and pet(s)."""
        schedule_pet = pet or self.pet

        if schedule_pet:
            all_tasks = schedule_pet.tasks
        else:
            all_tasks = self.owner.get_all_tasks()

        available_minutes = self.owner.available_hours_per_day * 60
        sorted_tasks = self.sort_tasks_by_priority(all_tasks)
        scheduled_tasks, dropped_tasks = self.fit_tasks_in_time(sorted_tasks, available_minutes)

        scheduled_task_objs = self._create_scheduled_tasks(scheduled_tasks, target_date)

        return DailySchedule(target_date, schedule_pet or (self.owner.pets[0] if self.owner.pets else None),
                           self.owner, scheduled_task_objs, dropped_tasks)

    def sort_tasks_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Returns tasks sorted by priority (high → medium → low)."""
        task_list = tasks if tasks is not None else self.tasks
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(task_list, key=lambda t: priority_order.get(t.priority, 3))

    def sort_tasks_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Returns tasks sorted by preferred time window (earliest first).
        Tasks without a time window appear last.
        Uses lambda to parse 'HH:MM' format strings into comparable integers.
        """
        task_list = tasks if tasks is not None else self.tasks

        def get_sort_key(task: Task) -> tuple:
            # If task has no preferred_time_window, push it to the end (infinity)
            if task.preferred_time_window is None:
                return (float('inf'), task.title)

            # Parse 'HH:MM' from the window start time into minutes since midnight
            start_time_str = task.preferred_time_window[0]
            hours, minutes = map(int, start_time_str.split(':'))
            time_in_minutes = hours * 60 + minutes

            return (time_in_minutes, task.title)

        return sorted(task_list, key=get_sort_key)

    def filter_tasks_by_status(
        self,
        tasks: Optional[List[Task]] = None,
        status: str = "pending"
    ) -> List[Task]:
        """
        Filters tasks by completion status.

        Args:
            tasks: Task list to filter (defaults to self.tasks)
            status: 'pending' for incomplete, 'completed' for done

        Returns:
            Filtered list of tasks
        """
        task_list = tasks if tasks is not None else self.tasks

        if status == "completed":
            return [t for t in task_list if t.completed]
        elif status == "pending":
            return [t for t in task_list if not t.completed]
        else:
            return task_list

    def filter_tasks_by_pet(
        self,
        pet: Pet,
        tasks: Optional[List[Task]] = None
    ) -> List[Task]:
        """
        Filters tasks by pet ownership.

        Args:
            pet: Pet to filter by
            tasks: Task list to filter (defaults to self.tasks)

        Returns:
            List of tasks for the given pet
        """
        task_list = tasks if tasks is not None else self.tasks
        return [t for t in task_list if t.pet == pet]

    def filter_tasks_by_status_and_pet(
        self,
        pet: Pet,
        status: str = "pending",
        tasks: Optional[List[Task]] = None
    ) -> List[Task]:
        """
        Filters tasks by both pet and completion status.

        Args:
            pet: Pet to filter by
            status: 'pending' or 'completed'
            tasks: Task list to filter (defaults to self.tasks)

        Returns:
            Filtered list of tasks matching both criteria
        """
        task_list = tasks if tasks is not None else self.tasks

        if status == "completed":
            return [t for t in task_list if t.pet == pet and t.completed]
        elif status == "pending":
            return [t for t in task_list if t.pet == pet and not t.completed]
        else:
            return [t for t in task_list if t.pet == pet]

    def fit_tasks_in_time(self, tasks: List[Task], available_minutes: int) -> tuple:
        """Returns (scheduled_tasks, dropped_tasks) where scheduled fit in available time.
        Low-priority tasks are dropped first if needed."""
        scheduled = []
        dropped = []
        used_minutes = 0

        for task in tasks:
            if used_minutes + task.duration_minutes <= available_minutes:
                scheduled.append(task)
                used_minutes += task.duration_minutes
            else:
                dropped.append(task)

        return (scheduled, dropped)

    def _create_scheduled_tasks(self, tasks: List[Task], target_date: date) -> List['ScheduledTask']:
        """Converts Task objects to ScheduledTask objects with time slots."""
        scheduled_tasks = []
        current_hour = 7
        current_minute = 0

        for task in tasks:
            start_time = f"{current_hour:02d}:{current_minute:02d}"
            current_minute += task.duration_minutes

            if current_minute >= 60:
                current_hour += current_minute // 60
                current_minute = current_minute % 60

            end_time = f"{current_hour:02d}:{current_minute:02d}"

            scheduled_tasks.append(ScheduledTask(task, start_time, end_time))

        return scheduled_tasks


class DailySchedule:
    """The output—a specific day's plan."""

    def __init__(self, date_obj: date, pet: Optional[Pet], owner: Owner, scheduled_tasks: Optional[List['ScheduledTask']] = None, dropped_tasks: Optional[List[Task]] = None):
        """Initialize a daily schedule with date, pet, owner, and task lists."""
        self.date = date_obj
        self.pet = pet
        self.owner = owner
        self.scheduled_tasks = scheduled_tasks or []
        self.dropped_tasks = dropped_tasks or []

    def get_total_duration(self) -> int:
        """Sums all task durations in minutes."""
        total = 0
        for scheduled_task in self.scheduled_tasks:
            total += scheduled_task.task.duration_minutes
        return total

    def display_plan(self) -> str:
        """Returns formatted schedule (e.g., '08:00 — Morning walk (30 min)')."""
        if not self.scheduled_tasks:
            return f"Schedule for {self.date}: No tasks scheduled."

        pet_info = f" for {self.pet.display_info()}" if self.pet else ""
        lines = [f"Schedule for {self.date}{pet_info}:"]

        for scheduled_task in self.scheduled_tasks:
            task = scheduled_task.task
            duration = task.duration_minutes
            time_range = scheduled_task.format_time()
            lines.append(f"  {time_range} — {task.title} ({duration} min) [{task.priority}]")

        total_duration = self.get_total_duration()
        lines.append(f"Total time: {total_duration} minutes")

        return "\n".join(lines)

    def explain_reasoning(self) -> str:
        """Returns why each task was chosen or dropped, including owner availability constraints."""
        available_minutes = self.owner.available_hours_per_day * 60
        used_minutes = self.get_total_duration()
        remaining_minutes = available_minutes - used_minutes

        lines = [f"Reasoning for {self.date}:"]
        lines.append(f"Owner availability: {self.owner.available_hours_per_day} hours ({available_minutes} minutes)")
        lines.append(f"Scheduled time: {used_minutes} minutes")
        lines.append(f"Remaining time: {remaining_minutes} minutes\n")

        if self.scheduled_tasks:
            lines.append("✓ Scheduled tasks:")
            for scheduled_task in self.scheduled_tasks:
                task = scheduled_task.task
                lines.append(f"  • {task.title} ({task.priority} priority, {task.duration_minutes} min)")
                if task.preferred_time_window:
                    lines.append(f"    Preferred window: {task.preferred_time_window}")

        if self.dropped_tasks:
            lines.append("\n✗ Dropped tasks (not enough time):")
            for task in self.dropped_tasks:
                lines.append(f"  • {task.title} ({task.priority} priority, {task.duration_minutes} min)")
        else:
            lines.append("\n✓ All tasks fit in available time!")

        return "\n".join(lines)


class ScheduledTask:
    """A task placed in a specific time slot on the schedule."""

    def __init__(self, task: Task, start_time: str, end_time: str, explanation: str = "", status: str = "scheduled"):
        """Initialize a scheduled task with timing and status information."""
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.explanation = explanation
        self.status = status  # scheduled, completed, skipped, rescheduled

    def get_duration(self) -> int:
        """Returns duration based on start and end times."""
        start_parts = self.start_time.split(":")
        end_parts = self.end_time.split(":")

        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])

        return end_minutes - start_minutes

    def format_time(self) -> str:
        """Returns formatted time range (e.g., '08:00—08:30')."""
        return f"{self.start_time}—{self.end_time}"
