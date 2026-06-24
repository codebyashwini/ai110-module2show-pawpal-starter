#!/usr/bin/env python3
"""
Test script demonstrating recurring task functionality.
Shows how daily and weekly tasks automatically create new instances when marked complete.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Setup
owner = Owner(name="Alice", available_hours_per_day=3)
pet = Pet(name="Mochi", species="golden retriever", owner=owner)
owner.add_pet(pet)
scheduler = Scheduler(owner, pet=pet)

# Test 1: Daily task
print("=" * 60)
print("TEST 1: Daily Task")
print("=" * 60)
daily_task = Task(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    recurring="daily",
    due_date=date(2026, 6, 23)  # Today
)
pet.add_task(daily_task)

print(f"Initial task count: {len(pet.tasks)}")
print(f"Task: {daily_task.title}")
print(f"Due date: {daily_task.due_date}")
print(f"Recurring: {daily_task.recurring}")
print(f"Completed: {daily_task.completed}\n")

# Mark as complete
next_task = scheduler.mark_task_complete(daily_task)

print(f"After marking complete:")
print(f"Task count: {len(pet.tasks)}")
print(f"Original task completed: {daily_task.completed}")
print(f"New task created: {next_task is not None}")
if next_task:
    print(f"  Title: {next_task.title}")
    print(f"  Due date: {next_task.due_date} (should be 2026-06-24)")
    print(f"  Completed: {next_task.completed}\n")

# Test 2: Weekly task
print("=" * 60)
print("TEST 2: Weekly Task")
print("=" * 60)
weekly_task = Task(
    title="Grooming",
    duration_minutes=60,
    priority="medium",
    recurring="weekly",
    due_date=date(2026, 6, 23)  # Today
)
pet.add_task(weekly_task)

print(f"Task count before: {len(pet.tasks)}")
print(f"Task: {weekly_task.title}")
print(f"Due date: {weekly_task.due_date}")
print(f"Recurring: {weekly_task.recurring}\n")

# Mark as complete
next_weekly = scheduler.mark_task_complete(weekly_task)

print(f"After marking complete:")
print(f"Task count: {len(pet.tasks)}")
print(f"Original task completed: {weekly_task.completed}")
print(f"New task created: {next_weekly is not None}")
if next_weekly:
    print(f"  Title: {next_weekly.title}")
    print(f"  Due date: {next_weekly.due_date} (should be 2026-06-30)")
    print(f"  Completed: {next_weekly.completed}\n")

# Test 3: One-time task
print("=" * 60)
print("TEST 3: One-time Task (should NOT create new instance)")
print("=" * 60)
onetime_task = Task(
    title="Vet appointment",
    duration_minutes=45,
    priority="high",
    recurring="one-time",
    due_date=date(2026, 6, 23)
)
pet.add_task(onetime_task)

initial_count = len(pet.tasks)
print(f"Task count before: {initial_count}")
print(f"Task: {onetime_task.title}")
print(f"Recurring: {onetime_task.recurring}\n")

# Mark as complete
result = scheduler.mark_task_complete(onetime_task)

print(f"After marking complete:")
print(f"Task count: {len(pet.tasks)}")
print(f"Original task completed: {onetime_task.completed}")
print(f"New task created: {result is not None} (should be False)")
