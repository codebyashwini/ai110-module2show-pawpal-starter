# PawPal+ Design Brainstorm

## Core Actions (What Users Can Do)

1. **Enter Pet & Owner Info** → System captures owner name, pet name/species, available daily hours
2. **Add & Manage Tasks** → User inputs task name, duration (minutes), priority (low/medium/high)
3. **Generate Schedule** → System orders tasks, fits them in available time, produces daily plan with explanations

---

## Building Blocks (Classes & Objects)

### **Owner**
**What it represents:** The person caring for the pet

**Attributes:**
- `name`: string
- `available_hours_per_day`: int
- `preferences`: dict (e.g., prefer mornings for walks)

**Methods:**
- `get_available_hours()` → returns minutes available
- `set_preferences(dict)` → updates owner preferences

---

### **Pet**
**What it represents:** The animal being cared for

**Attributes:**
- `name`: string
- `species`: string (dog, cat, etc.)
- `owner`: Owner (reference)

**Methods:**
- `get_owner()` → returns the Owner object
- `display_info()` → returns string like "Mochi (golden retriever)"

---

### **Task**
**What it represents:** A single care activity (walk, feeding, meds, etc.)

**Attributes:**
- `title`: string (e.g., "Morning walk")
- `duration_minutes`: int
- `priority`: string (low/medium/high)
- `recurring`: string (daily, weekly, or one-time)

**Methods:**
- `get_duration()` → returns int
- `get_priority()` → returns priority level

---

### **Scheduler**
**What it represents:** The engine that produces daily plans

**Attributes:**
- `owner`: Owner
- `pet`: Pet
- `tasks`: list of Task objects

**Methods:**
- `generate_schedule()` → returns a DailySchedule
- `sort_tasks_by_priority()` → returns tasks ordered by priority
- `fit_tasks_in_time(tasks, available_minutes)` → returns tasks that fit, dropping low-priority ones if needed

---

### **DailySchedule**
**What it represents:** The output—a specific day's plan

**Attributes:**
- `date`: date object
- `pet`: Pet
- `scheduled_tasks`: list of ScheduledTask objects
- `total_duration_minutes`: int

**Methods:**
- `get_total_duration()` → sums all task durations
- `display_plan()` → returns formatted schedule (e.g., "08:00 — Morning walk (30 min)")
- `explain_reasoning()` → returns why each task was chosen/dropped

---

### **ScheduledTask**
**What it represents:** A task placed in a specific time slot on the schedule

**Attributes:**
- `task`: Task (reference)
- `start_time`: string (e.g., "08:00")
- `end_time`: string (e.g., "08:30")
- `explanation`: string (e.g., "High priority, fits available time")

**Methods:**
- `get_duration()` → returns end - start
- `format_time()` → returns "08:00—08:30"

---

## Relationships

```
Owner has many Pets
Pet needs many Tasks
Scheduler plans for one Owner and one Pet
Scheduler consumes many Tasks and generates one DailySchedule
DailySchedule contains many ScheduledTasks
ScheduledTask wraps a Task with timing info
```

---

## Next Steps

1. **Create Python class stubs** — define each class with attributes and method signatures (no logic yet)
2. **Implement scheduling logic** — start with sorting by priority, then fit into available time
3. **Add edge case handling** — what if total task time > available time? What about task conflicts?
4. **Connect to Streamlit UI** — feed user inputs into your Scheduler, display the resulting DailySchedule
5. **Write tests** — verify sorting, time-fitting, and edge cases work correctly
6. **Update UML** — refine the diagram to match what you actually built
