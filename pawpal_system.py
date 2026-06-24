"""
PawPal+ Backend Logic Layer
Classes for managing pets, owners, tasks, and scheduling.
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from itertools import combinations


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

    def to_dict(self) -> Dict:
        """Converts Owner to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "available_hours_per_day": self.available_hours_per_day,
            "preferences": self.preferences,
            "pets": [pet.to_dict() for pet in self.pets]
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Owner':
        """Reconstructs Owner from a dictionary."""
        owner = Owner(
            name=data["name"],
            available_hours_per_day=data["available_hours_per_day"],
            preferences=data.get("preferences", {})
        )
        # Pets will be set via Pet.from_dict() to maintain circular references
        for pet_data in data.get("pets", []):
            pet = Pet.from_dict(pet_data, owner)
            owner.add_pet(pet)
        return owner


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

    def to_dict(self) -> Dict:
        """Converts Pet to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks]
        }

    @staticmethod
    def from_dict(data: Dict, owner: Owner) -> 'Pet':
        """Reconstructs Pet from a dictionary. Owner must be provided to restore the reference."""
        pet = Pet(name=data["name"], species=data["species"], owner=owner)
        for task_data in data.get("tasks", []):
            task = Task.from_dict(task_data)
            pet.add_task(task)
        return pet


@dataclass
class Task:
    """Represents a single care activity."""
    title: str
    duration_minutes: int
    priority: str  # low, medium, high
    pet: Optional['Pet'] = None  # which pet this task is for
    recurring: str = "one-time"  # daily, weekly, one-time
    due_date: Optional[date] = None  # when this task is due
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

    def to_dict(self) -> Dict:
        """Converts Task to a dictionary for JSON serialization. Dates are converted to ISO format strings."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "recurring": self.recurring,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "preferred_time_window": self.preferred_time_window,
            "completed": self.completed
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        """Reconstructs Task from a dictionary. Converts ISO date strings back to date objects."""
        due_date = None
        if data.get("due_date"):
            due_date = date.fromisoformat(data["due_date"])

        preferred_time_window = None
        if data.get("preferred_time_window"):
            window = data["preferred_time_window"]
            preferred_time_window = tuple(window) if isinstance(window, list) else window

        return Task(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            recurring=data.get("recurring", "one-time"),
            due_date=due_date,
            preferred_time_window=preferred_time_window,
            completed=data.get("completed", False)
        )


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
        sorted_tasks = self.sort_tasks_by_priority_then_time(all_tasks)
        scheduled_tasks, dropped_tasks = self.fit_tasks_in_time(sorted_tasks, available_minutes)

        scheduled_task_objs = self._create_scheduled_tasks(scheduled_tasks, target_date)

        return DailySchedule(target_date, schedule_pet or (self.owner.pets[0] if self.owner.pets else None),
                           self.owner, scheduled_task_objs, dropped_tasks)

    def sort_tasks_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sort tasks by priority level in descending order of importance.

        Sorts tasks into high → medium → low priority, preserving relative order
        within each priority tier (stable sort). Used by generate_schedule to
        prioritize critical tasks when available time is limited.

        Args:
            tasks: Task list to sort (defaults to self.tasks)

        Returns:
            Sorted list of tasks (highest priority first)
        """
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

    def sort_tasks_by_priority_then_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sort tasks by priority first (high → medium → low), then by time within each priority tier.

        This is the primary scheduling algorithm: critical tasks are scheduled first,
        and within each priority level, tasks with earlier preferred time windows are
        prioritized. Tasks without a time window appear last within their priority tier.

        Args:
            tasks: Task list to sort (defaults to self.tasks)

        Returns:
            Sorted list of tasks (highest priority first, earliest time second)
        """
        task_list = tasks if tasks is not None else self.tasks
        priority_order = {"high": 0, "medium": 1, "low": 2}

        def get_sort_key(task: Task) -> tuple:
            priority_rank = priority_order.get(task.priority, 3)

            # Extract time for secondary sort within each priority tier
            if task.preferred_time_window is None:
                time_in_minutes = float('inf')
            else:
                start_time_str = task.preferred_time_window[0]
                hours, minutes = map(int, start_time_str.split(':'))
                time_in_minutes = hours * 60 + minutes

            return (priority_rank, time_in_minutes, task.title)

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

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Marks a task as complete and creates a new instance for the next occurrence if recurring.

        Args:
            task: The task to mark complete

        Returns:
            The newly created task if recurring, None otherwise
        """
        task.mark_complete()

        if task.recurring == "one-time":
            return None

        if not task.pet or not task.due_date:
            return None

        # Calculate next due date based on recurring frequency
        if task.recurring == "daily":
            next_due_date = task.due_date + timedelta(days=1)
        elif task.recurring == "weekly":
            next_due_date = task.due_date + timedelta(weeks=1)
        else:
            return None

        # Create a new task instance for the next occurrence
        next_task = Task(
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            pet=task.pet,
            recurring=task.recurring,
            due_date=next_due_date,
            preferred_time_window=task.preferred_time_window,
            completed=False
        )

        # Add the new task to the pet's task list
        task.pet.add_task(next_task)

        return next_task

    def fit_tasks_in_time(self, tasks: List[Task], available_minutes: int) -> tuple:
        """
        Greedily fit tasks into available time, dropping tasks that don't fit.

        Iterates through tasks in order and schedules each one if it fits within
        the available time budget. Tasks that exceed remaining time are dropped.
        Caller should pre-sort tasks by priority to ensure critical tasks are
        scheduled first.

        Args:
            tasks: Task list to fit (expected to be pre-sorted by priority)
            available_minutes: Total minutes available in the day

        Returns:
            Tuple of (scheduled_tasks, dropped_tasks) lists
        """
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

    def find_next_available_slot(self, task: Task, tasks: Optional[List[Task]] = None) -> Optional[tuple]:
        """
        Finds the next available time slot for a task that avoids conflicts.

        Scans through the day in 15-minute intervals starting at 7:00 AM,
        checking if the proposed task duration can fit without overlapping
        any existing tasks' preferred time windows. Returns the first available
        (start_time, end_time) tuple or None if no slot found before 11:00 PM.

        This algorithm is useful for:
        - Finding flexible scheduling options for tasks without fixed windows
        - Proposing alternative times when a preferred window has conflicts
        - Checking feasibility when time gaps are fragmented

        Args:
            task: Task object to find a slot for
            tasks: List of existing tasks to check for conflicts (defaults to self.tasks)

        Returns:
            Tuple of (start_time_str, end_time_str) if slot found, None otherwise
        """
        task_list = tasks if tasks is not None else self.tasks
        duration = task.duration_minutes

        # Scan the day in 15-minute intervals from 7:00 AM to 11:00 PM
        start_hour = 7
        start_minute = 0
        end_hour = 23
        end_minute = 0

        current_minutes = start_hour * 60 + start_minute
        max_minutes = end_hour * 60 + end_minute

        while current_minutes + duration <= max_minutes:
            # Convert minutes to HH:MM format
            hours = current_minutes // 60
            minutes = current_minutes % 60
            test_start = f"{hours:02d}:{minutes:02d}"

            # Calculate end time
            end_minutes = current_minutes + duration
            end_hours = end_minutes // 60
            end_mins = end_minutes % 60
            test_end = f"{end_hours:02d}:{end_mins:02d}"

            test_window = (test_start, test_end)

            # Check if this window conflicts with any existing task
            has_conflict = False
            for existing_task in task_list:
                if existing_task.preferred_time_window:
                    if self._times_overlap(test_window, existing_task.preferred_time_window):
                        has_conflict = True
                        break

            if not has_conflict:
                return (test_start, test_end)

            # Move forward by 15 minutes
            current_minutes += 15

        return None

    def _time_to_minutes(self, time_str: str) -> int:
        """Converts time string 'HH:MM' to minutes since midnight."""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def _get_pet_name(self, task: Task) -> str:
        """Get pet name, with fallback for missing pets."""
        return task.pet.name if task.pet else "Unknown Pet"

    def _times_overlap(self, window1: tuple, window2: tuple) -> bool:
        """
        Check if two time windows overlap.

        Args:
            window1: Tuple of (start_time_str, end_time_str) e.g., ("07:00", "08:00")
            window2: Tuple of (start_time_str, end_time_str)

        Returns:
            True if windows overlap, False otherwise
        """
        start1, end1 = window1
        start2, end2 = window2

        start1_min = self._time_to_minutes(start1)
        end1_min = self._time_to_minutes(end1)
        start2_min = self._time_to_minutes(start2)
        end2_min = self._time_to_minutes(end2)

        return start1_min < end2_min and start2_min < end1_min

    def _tasks_have_conflicting_times(self, task1: Task, task2: Task) -> bool:
        """
        Check if two tasks have overlapping preferred time windows.

        Both tasks must have time windows defined to be considered for conflict.
        Returns False if either task lacks a preferred_time_window.

        Args:
            task1: First task to compare
            task2: Second task to compare

        Returns:
            True if both tasks have time windows and they overlap, False otherwise
        """
        return (
            task1.preferred_time_window and
            task2.preferred_time_window and
            self._times_overlap(task1.preferred_time_window, task2.preferred_time_window)
        )

    def _format_conflict_warning(self, task1: Task, task2: Task) -> str:
        """Format a conflict warning message."""
        pet1_name = self._get_pet_name(task1)
        pet2_name = self._get_pet_name(task2)
        start1, end1 = task1.preferred_time_window
        start2, end2 = task2.preferred_time_window

        return (
            f"⚠️  TIME CONFLICT: '{task1.title}' ({pet1_name}) "
            f"[{start1}–{end1}] "
            f"overlaps with '{task2.title}' ({pet2_name}) "
            f"[{start2}–{end2}]"
        )

    def detect_time_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """
        Detect if any two tasks have overlapping preferred time windows.

        Returns a list of warning messages rather than raising exceptions.
        This is a lightweight conflict detection strategy that allows
        scheduling to proceed while alerting the user to conflicts.

        Args:
            tasks: Task list to check (defaults to self.tasks)

        Returns:
            List of warning strings describing conflicts
        """
        task_list = tasks if tasks is not None else self.tasks
        warnings = []

        for task1, task2 in combinations(task_list, 2):
            if self._tasks_have_conflicting_times(task1, task2):
                warnings.append(self._format_conflict_warning(task1, task2))

        return warnings

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


def save_to_json(owner: Owner, filepath: str = "data.json") -> None:
    """
    Saves the owner, pets, and tasks to a JSON file.

    Converts the Owner object and all its related pets and tasks to a dictionary,
    then writes to JSON. Uses ISO format for date serialization.

    Args:
        owner: The Owner object to save
        filepath: Path where the JSON file will be written (default: "data.json")
    """
    with open(filepath, 'w') as f:
        json.dump(owner.to_dict(), f, indent=2)


def load_from_json(filepath: str = "data.json") -> Optional[Owner]:
    """
    Loads owner, pets, and tasks from a JSON file.

    Reads a JSON file and reconstructs the Owner object with all related pets
    and tasks. Handles date deserialization from ISO format strings.

    Args:
        filepath: Path to the JSON file to load (default: "data.json")

    Returns:
        The reconstructed Owner object, or None if file doesn't exist or is invalid
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Owner.from_dict(data)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading data from {filepath}: {e}")
        return None
