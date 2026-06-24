# Recurring Tasks Implementation Guide

## Overview
This implementation adds automatic recurring task creation to the PawPal system. When a "daily" or "weekly" task is marked complete, a new instance is automatically created for the next occurrence.

## Changes Made

### 1. **Import Addition** (`pawpal_system.py`)
Added `timedelta` to the imports to support date arithmetic:
```python
from datetime import date, datetime, timedelta
```

### 2. **Task Class Enhancement** (`pawpal_system.py`)
Added a new `due_date` field to track when a task is due:
```python
@dataclass
class Task:
    # ... existing fields ...
    due_date: Optional[date] = None  # when this task is due
```

### 3. **Scheduler.mark_task_complete() Method** (`pawpal_system.py`)
Created a new method in the Scheduler class that:
- Marks a task as complete
- Automatically creates a new instance if the task is recurring
- Uses `timedelta` to calculate the next due date

```python
def mark_task_complete(self, task: Task) -> Optional[Task]:
    """
    Marks a task as complete and creates a new instance for the next occurrence if recurring.
    """
    task.mark_complete()
    
    if task.recurring == "one-time":
        return None
    
    if not task.pet or not task.due_date:
        return None
    
    # Calculate next due date
    if task.recurring == "daily":
        next_due_date = task.due_date + timedelta(days=1)
    elif task.recurring == "weekly":
        next_due_date = task.due_date + timedelta(weeks=1)
    else:
        return None
    
    # Create and add new task
    next_task = Task(...)
    task.pet.add_task(next_task)
    
    return next_task
```

## How It Works

### Daily Tasks
When a daily task is marked complete:
- Original task: `due_date = 2026-06-23` → marked as `completed = True`
- New task automatically created: `due_date = 2026-06-24` (today + 1 day)

**Python timedelta example:**
```python
today = date(2026, 6, 23)
tomorrow = today + timedelta(days=1)  # 2026-06-24
```

### Weekly Tasks
When a weekly task is marked complete:
- Original task: `due_date = 2026-06-23` → marked as `completed = True`
- New task automatically created: `due_date = 2026-06-30` (today + 7 days)

**Python timedelta example:**
```python
today = date(2026, 6, 23)
next_week = today + timedelta(weeks=1)  # 2026-06-30
```

### One-Time Tasks
One-time tasks are marked complete but NO new instance is created:
```python
task.recurring = "one-time"  # Returns None, no new task created
```

## Usage Example

```python
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Setup
owner = Owner(name="Alice", available_hours_per_day=3)
pet = Pet(name="Mochi", species="golden retriever", owner=owner)
scheduler = Scheduler(owner, pet=pet)

# Create a daily task
daily_task = Task(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    recurring="daily",
    due_date=date(2026, 6, 23)
)
pet.add_task(daily_task)

# Mark as complete - automatically creates next occurrence
next_task = scheduler.mark_task_complete(daily_task)
# next_task.due_date = date(2026, 6, 24)
# Original task has completed = True
# New task has completed = False
```

## Key Design Decisions

1. **Method Location**: The `mark_task_complete()` method is in the `Scheduler` class (not directly on `Task`) because:
   - The scheduler manages the business logic of task scheduling
   - It has access to the pet and owner context
   - It keeps concerns properly separated

2. **Backward Compatibility**: The original `Task.mark_complete()` method still exists and works as before. The new `mark_task_complete()` in Scheduler is the recommended approach for handling recurring tasks.

3. **Required Fields**: The method checks that both `task.pet` and `task.due_date` exist before creating a new task, preventing errors from incomplete task definitions.

4. **New Task Properties**: The new recurring task inherits:
   - Same title, duration, priority
   - Same recurring frequency
   - Same preferred time window (if set)
   - Reset to `completed = False`

## Testing

All existing tests pass, and the implementation has been verified with test cases for:
- ✅ Daily task recurrence (due_date + 1 day)
- ✅ Weekly task recurrence (due_date + 7 days)  
- ✅ One-time tasks (no new instance created)
- ✅ Backward compatibility with existing code

Run the test suite with:
```bash
python -m pytest tests/test_pawpal.py -v
```
