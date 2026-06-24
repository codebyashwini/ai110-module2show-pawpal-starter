"""
PawPal+ Testing Script
Demonstrates creating owners, pets, tasks, and testing sorting/filtering methods.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Create an Owner
owner = Owner(name="Alice", available_hours_per_day=4)
print(f"Created owner: {owner.name} with {owner.available_hours_per_day} hours available per day\n")

# Create Pets
pet1 = Pet(name="Mochi", species="Golden Retriever", owner=owner)
pet2 = Pet(name="Whiskers", species="Tabby Cat", owner=owner)

owner.add_pet(pet1)
owner.add_pet(pet2)
print(f"Created pets: {pet1.display_info()}, {pet2.display_info()}\n")

# Add tasks to pet1 (Mochi) - OUT OF ORDER to test sorting
task1 = Task(
    title="Training Session",
    duration_minutes=30,
    priority="medium",
    preferred_time_window=("15:00", "17:00"),
    recurring="daily"
)
pet1.add_task(task1)

task2 = Task(
    title="Evening Snack",
    duration_minutes=10,
    priority="low",
    preferred_time_window=("18:00", "19:00"),
    recurring="daily"
)
pet1.add_task(task2)

task3 = Task(
    title="Morning Walk",
    duration_minutes=45,
    priority="high",
    preferred_time_window=("07:00", "09:00"),
    recurring="daily"
)
pet1.add_task(task3)

task4 = Task(
    title="Breakfast",
    duration_minutes=15,
    priority="high",
    recurring="daily"
)
pet1.add_task(task4)

# Add tasks to pet2 (Whiskers) - OUT OF ORDER
task5 = Task(
    title="Play Time",
    duration_minutes=20,
    priority="medium",
    preferred_time_window=("14:00", "16:00")
)
pet2.add_task(task5)

task6 = Task(
    title="Litter Box Cleaning",
    duration_minutes=15,
    priority="medium",
    recurring="daily"
)
pet2.add_task(task6)

task7 = Task(
    title="Feeding",
    duration_minutes=10,
    priority="high",
    recurring="daily"
)
pet2.add_task(task7)

# Mark one task as completed to test filtering
task2.mark_complete()

print("\n" + "=" * 60)
print("TEST 1: SORT BY TIME")
print("=" * 60)

scheduler = Scheduler(owner)
all_tasks = owner.get_all_tasks()

print("\nAll tasks (in original order):")
for i, task in enumerate(all_tasks, 1):
    pet_name = task.pet.name if task.pet else "Unknown"
    time_info = task.preferred_time_window if task.preferred_time_window else "No time window"
    print(f"  {i}. {task.title} ({pet_name}) - {time_info}")

sorted_by_time = scheduler.sort_tasks_by_time(all_tasks)
print("\nTasks sorted by time (earliest first):")
for i, task in enumerate(sorted_by_time, 1):
    pet_name = task.pet.name if task.pet else "Unknown"
    time_info = task.preferred_time_window if task.preferred_time_window else "No time window"
    print(f"  {i}. {task.title} ({pet_name}) - {time_info}")

print("\n" + "=" * 60)
print("TEST 2: FILTER BY STATUS")
print("=" * 60)

pending_tasks = scheduler.filter_tasks_by_status(all_tasks, status="pending")
completed_tasks = scheduler.filter_tasks_by_status(all_tasks, status="completed")

print(f"\nPending tasks ({len(pending_tasks)}):")
for i, task in enumerate(pending_tasks, 1):
    pet_name = task.pet.name if task.pet else "Unknown"
    print(f"  {i}. {task.title} ({pet_name}) - Priority: {task.priority}")

print(f"\nCompleted tasks ({len(completed_tasks)}):")
for i, task in enumerate(completed_tasks, 1):
    pet_name = task.pet.name if task.pet else "Unknown"
    print(f"  {i}. {task.title} ({pet_name}) - Priority: {task.priority}")

print("\n" + "=" * 60)
print("TEST 3: FILTER BY PET")
print("=" * 60)

mochi_tasks = scheduler.filter_tasks_by_pet(pet1, all_tasks)
whiskers_tasks = scheduler.filter_tasks_by_pet(pet2, all_tasks)

print(f"\nTasks for {pet1.name} ({len(mochi_tasks)}):")
for i, task in enumerate(mochi_tasks, 1):
    status = "✓ Completed" if task.completed else "○ Pending"
    print(f"  {i}. {task.title} - {status}")

print(f"\nTasks for {pet2.name} ({len(whiskers_tasks)}):")
for i, task in enumerate(whiskers_tasks, 1):
    status = "✓ Completed" if task.completed else "○ Pending"
    print(f"  {i}. {task.title} - {status}")

print("\n" + "=" * 60)
print("TEST 4: FILTER BY STATUS AND PET")
print("=" * 60)

mochi_pending = scheduler.filter_tasks_by_status_and_pet(pet1, status="pending", tasks=all_tasks)
whiskers_pending = scheduler.filter_tasks_by_status_and_pet(pet2, status="pending", tasks=all_tasks)

print(f"\nPending tasks for {pet1.name} ({len(mochi_pending)}):")
for i, task in enumerate(mochi_pending, 1):
    print(f"  {i}. {task.title}")

print(f"\nPending tasks for {pet2.name} ({len(whiskers_pending)}):")
for i, task in enumerate(whiskers_pending, 1):
    print(f"  {i}. {task.title}")

print("\n" + "=" * 60)
print("TODAY'S SCHEDULE")
print("=" * 60)

# Generate schedule for today
today = date.today()
daily_schedule = scheduler.generate_schedule(today)

# Display the schedule
print("\n" + daily_schedule.display_plan())

# Show reasoning
print("\n" + daily_schedule.explain_reasoning())

print("\n" + "=" * 60)
