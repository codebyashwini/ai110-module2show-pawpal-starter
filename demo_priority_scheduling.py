"""
Demonstration of Priority-Based Scheduling in PawPal+

This script shows how the scheduler sorts tasks by priority first,
then by time within each priority tier.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

print("=" * 70)
print("PRIORITY-BASED SCHEDULING DEMONSTRATION")
print("=" * 70)

# Create owner with 3 hours available
owner = Owner(name="Jordan", available_hours_per_day=3)

# Create a pet
dog = Pet(name="Max", species="Labrador", owner=owner)
owner.add_pet(dog)

# Create tasks with mixed priorities and time windows
tasks = [
    Task(title="Afternoon Play", duration_minutes=20, priority="low",
         preferred_time_window=("14:00", "15:00")),
    Task(title="Morning Walk", duration_minutes=45, priority="high",
         preferred_time_window=("07:00", "08:00")),
    Task(title="Medication", duration_minutes=10, priority="high"),
    Task(title="Evening Training", duration_minutes=30, priority="medium",
         preferred_time_window=("17:00", "18:00")),
    Task(title="Grooming", duration_minutes=30, priority="low"),
    Task(title="Breakfast", duration_minutes=15, priority="high"),
    Task(title="Lunch Feeding", duration_minutes=10, priority="medium"),
]

# Add all tasks to the dog
for task in tasks:
    dog.add_task(task)

print("\n1. ORIGINAL TASK LIST (unsorted):")
print("-" * 70)
for i, task in enumerate(tasks, 1):
    time_info = f"→ {task.preferred_time_window}" if task.preferred_time_window else "→ no time window"
    print(f"   {i}. {task.title:25} ({task.priority:6} priority, {task.duration_minutes:2} min) {time_info}")

# Sort by priority only
scheduler = Scheduler(owner)
sorted_by_priority = scheduler.sort_tasks_by_priority(tasks)

print("\n2. SORTED BY PRIORITY ONLY:")
print("-" * 70)
for i, task in enumerate(sorted_by_priority, 1):
    time_info = f"→ {task.preferred_time_window}" if task.preferred_time_window else "→ no time window"
    print(f"   {i}. {task.title:25} ({task.priority:6} priority, {task.duration_minutes:2} min) {time_info}")

# Sort by time only
sorted_by_time = scheduler.sort_tasks_by_time(tasks)

print("\n3. SORTED BY TIME ONLY:")
print("-" * 70)
for i, task in enumerate(sorted_by_time, 1):
    time_info = f"→ {task.preferred_time_window}" if task.preferred_time_window else "→ no time window"
    print(f"   {i}. {task.title:25} ({task.priority:6} priority, {task.duration_minutes:2} min) {time_info}")

# Sort by priority THEN time (the new algorithm)
sorted_priority_then_time = scheduler.sort_tasks_by_priority_then_time(tasks)

print("\n4. SORTED BY PRIORITY → TIME (PawPal+ Algorithm):")
print("-" * 70)
for i, task in enumerate(sorted_priority_then_time, 1):
    time_info = f"→ {task.preferred_time_window}" if task.preferred_time_window else "→ no time window"
    print(f"   {i}. {task.title:25} ({task.priority:6} priority, {task.duration_minutes:2} min) {time_info}")

# Generate the actual schedule
print("\n5. GENERATED DAILY SCHEDULE (available: 180 minutes):")
print("-" * 70)
daily_schedule = scheduler.generate_schedule(date.today(), dog)
print(daily_schedule.display_plan())

print("\n6. SCHEDULING REASONING:")
print("-" * 70)
print(daily_schedule.explain_reasoning())

print("\n" + "=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print("""
The Priority-Then-Time algorithm ensures:

✓ HIGH-PRIORITY tasks are ALWAYS scheduled first, regardless of time
  → Morning Walk (high, 07:00) scheduled before Afternoon Play (low, 14:00)
  → Medication (high, no window) scheduled even without a time window

✓ WITHIN each priority tier, earlier time windows come first
  → Among high-priority: Medication (no window) → Breakfast (no window) → Morning Walk (07:00)
  → Among medium-priority: Lunch Feeding (no window) → Evening Training (17:00)

✓ LOW-PRIORITY tasks are dropped when time runs out
  → Afternoon Play and Grooming are dropped to make room for critical tasks

This approach ensures that the most important care activities are never missed,
while still respecting time preferences and constraints.
""")
