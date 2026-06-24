"""
PawPal+ Backend Logic Layer
Classes for managing pets, owners, tasks, and scheduling.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Optional


class Owner:
    """Represents the person caring for the pet."""

    def __init__(self, name: str, available_hours_per_day: int, preferences: Optional[Dict] = None):
        self.name = name
        self.available_hours_per_day = available_hours_per_day
        self.preferences = preferences or {}

    def get_available_hours(self) -> int:
        """Returns available hours per day."""
        pass

    def set_preferences(self, preferences: Dict) -> None:
        """Updates owner preferences."""
        pass


@dataclass
class Pet:
    """Represents the animal being cared for."""
    name: str
    species: str
    owner: Owner

    def get_owner(self) -> Owner:
        """Returns the Owner object."""
        pass

    def display_info(self) -> str:
        """Returns formatted pet info (e.g., 'Mochi (golden retriever)')."""
        pass


@dataclass
class Task:
    """Represents a single care activity."""
    title: str
    duration_minutes: int
    priority: str  # low, medium, high
    pet: Optional['Pet'] = None  # which pet this task is for
    recurring: str = "one-time"  # daily, weekly, one-time
    preferred_time_window: Optional[tuple] = None  # e.g., ("07:00", "09:00") for time-specific tasks

    def get_duration(self) -> int:
        """Returns task duration in minutes."""
        pass

    def get_priority(self) -> str:
        """Returns priority level."""
        pass


class Scheduler:
    """The engine that produces daily plans."""

    def __init__(self, owner: Owner, pet: Pet, tasks: Optional[List[Task]] = None):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks or []

    def generate_schedule(self, target_date: date) -> 'DailySchedule':
        """Returns a DailySchedule for the given date, owner, and pet."""
        pass

    def sort_tasks_by_priority(self) -> List[Task]:
        """Returns tasks sorted by priority (high → medium → low)."""
        pass

    def fit_tasks_in_time(self, tasks: List[Task], available_minutes: int) -> tuple:
        """Returns (scheduled_tasks, dropped_tasks) where scheduled fit in available time.
        Low-priority tasks are dropped first if needed."""
        pass


class DailySchedule:
    """The output—a specific day's plan."""

    def __init__(self, date_obj: date, pet: Pet, owner: Owner, scheduled_tasks: Optional[List['ScheduledTask']] = None, dropped_tasks: Optional[List[Task]] = None):
        self.date = date_obj
        self.pet = pet
        self.owner = owner
        self.scheduled_tasks = scheduled_tasks or []
        self.dropped_tasks = dropped_tasks or []

    def get_total_duration(self) -> int:
        """Sums all task durations in minutes."""
        pass

    def display_plan(self) -> str:
        """Returns formatted schedule (e.g., '08:00 — Morning walk (30 min)')."""
        pass

    def explain_reasoning(self) -> str:
        """Returns why each task was chosen or dropped, including owner availability constraints."""
        pass


class ScheduledTask:
    """A task placed in a specific time slot on the schedule."""

    def __init__(self, task: Task, start_time: str, end_time: str, explanation: str = "", status: str = "scheduled"):
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.explanation = explanation
        self.status = status  # scheduled, completed, skipped, rescheduled

    def get_duration(self) -> int:
        """Returns duration based on start and end times."""
        pass

    def format_time(self) -> str:
        """Returns formatted time range (e.g., '08:00—08:30')."""
        pass
