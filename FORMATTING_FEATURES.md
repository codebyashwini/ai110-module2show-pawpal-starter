# PawPal+ User-Friendly Output Formatting

## Overview

PawPal+ now includes enhanced visual formatting to make output more readable and engaging. This document details the formatting enhancements added to the application.

## Features Implemented

### 1. Color-Coded Priority Indicators

**Function**: `format_priority_indicator(priority: str) -> str`

Displays task priorities with color codes and emojis:
- 🔴 **HIGH** (bright red, ANSI code 91)
- 🟡 **MEDIUM** (bright yellow, ANSI code 93)
- 🟢 **LOW** (bright green, ANSI code 92)

Used in:
- Task list tables
- Schedule display
- Summary statistics

### 2. Status Badges with Emojis

**Function**: `format_status_badge(status: str) -> str`

Displays task status with visual indicators:
- ✅ **COMPLETED** — Task finished
- ⏳ **PENDING** — Task awaiting action
- 📌 **SCHEDULED** — Task in schedule
- ⏭️ **SKIPPED** — Task not completed
- 🔄 **RESCHEDULED** — Task moved to different time

### 3. Task Type Emojis

**Function**: `get_task_emoji(task_title: str) -> str`

Automatically infers task type from title and assigns emoji:
- 🚶 walk
- 🍽️ feed
- 🎾 play
- ✂️ groom
- 💊 vet/medication
- 😴 sleep
- 🚿 bath
- 🎓 train/training
- 💪 exercise
- 🤗 cuddle
- 📝 (default for unrecognized tasks)

### 4. Pet Species Emojis

**Function**: `get_species_emoji(species: str) -> str`

Displays pet type with appropriate emoji:
- 🐕 dog
- 🐈 cat
- 🐰 rabbit
- 🦜 bird
- 🐹 hamster/guinea pig
- 🐠 fish
- 🐢 turtle
- 🐾 other/unknown

### 5. Structured ASCII Tables

**Library**: `tabulate` (v0.9.0+)

Generates professional, formatted tables with multiple styles:

#### Task List Table
**Function**: `format_task_list_table(tasks: List[Dict], use_color: bool = True) -> str`

Uses `tabulate` with "grid" format. Displays:
- Status (with emoji badge)
- Pet name (with species emoji)
- Task title (with task type emoji)
- Duration
- Priority (with color coding)
- Time window (or "Flexible")

Example output:
```
+--------------+-------------+-----------------+----------+------------+-------------+
| Status       | Pet         | Task            | Duration | Priority   | Time Window |
+==============+=============+=================+==========+============+=============+
| ⏳ PENDING   | 🐕 Mochi    | 🚶 Morning walk | 30 min   | 🔴 HIGH   | 07:00—09:00 |
+--------------+-------------+-----------------+----------+------------+-------------+
```

#### Schedule Table
**Function**: `format_schedule_table(scheduled_tasks: List[Dict]) -> str`

Uses `tabulate` with "fancy_grid" format. Displays:
- Time slot (⏰)
- Task name (📝 with emoji)
- Pet (🐾 with emoji)
- Duration (⏱️)
- Priority (⭐)

Example output:
```
╒════════════╤═════════════════╤═════════╤════════════╤═══════════╕
│ ⏰ Time    │ 📝 Task         │ 🐾 Pet  │ ⏱️ Duration │ ⭐ Priority │
╞════════════╪═════════════════╪═════════╪════════════╪═══════════╡
│ 07:00—07:30│ 🚶 Morning walk │ 🐕 Mochi│ 30 min     │ HIGH      │
├────────────┼─────────────────┼─────────┼────────────┼───────────┤
│ 07:30—08:00│ 🍽️ Feeding      │ 🐕 Mochi│ 30 min     │ HIGH      │
╘════════════╧═════════════════╧═════════╧════════════╧═══════════╛
```

#### Pet Summary Table
**Function**: `format_pet_summary_table(pets: List[Dict]) -> str`

Uses `tabulate` with "rounded_grid" format. Displays:
- Pet name (with species emoji)
- Species
- Task count (with 📋 indicator)

Example output:
```
╭─────────────┬───────────┬─────────────╮
│ 🐾 Pet      │ Species   │ Tasks       │
├─────────────┼───────────┼─────────────┤
│ 🐕 Mochi    │ Dog       │ 📋 5 tasks  │
├─────────────┼───────────┼─────────────┤
│ 🐈 Whiskers │ Cat       │ 📋 3 tasks  │
╰─────────────┴───────────┴─────────────╯
```

### 6. Summary Statistics Display

**Function**: `format_summary_stats(total_tasks, completed_tasks, dropped_tasks, used_minutes, available_minutes) -> str`

Creates formatted statistics summary showing:
- Completion rate (percentage)
- Pending task count
- Dropped task count
- Time utilization (percentage)
- Remaining time

Example output:
```
==================================================
📊 SCHEDULE SUMMARY
==================================================
✅ Completed:      2/5 (40.0%)
⏳ Pending:        3
⏭️  Dropped:        1
--------------------------------------------------
⏱️  Time Used:       120/240 minutes (50.0%)
🕐 Time Remaining: 120 minutes
==================================================
```

### 7. Conflict Warning Formatting

**Function**: `format_conflict_warning(task1_title, task1_pet, task1_window, task2_title, task2_pet, task2_window) -> str`

Formats time conflict warnings with:
- ⚠️ warning header
- Task emoji and name
- Pet identification
- Time window for each conflicting task

### 8. Message Helpers

Simple emoji-prefixed message formatters:
- `format_success_message(message)` → ✅ prefix
- `format_warning_message(message)` → ⚠️ prefix
- `format_info_message(message)` → ℹ️ prefix
- `format_error_message(message)` → ❌ prefix

## Files Modified

### New Files
- **`formatting_utils.py`** — Complete formatting utilities module
  - 400+ lines of formatting functions
  - All emoji mappings and color definitions
  - Table formatting with tabulate

### Updated Files
- **`app.py`** — Integrated formatting functions
  - Pet display now uses `format_pet_summary_table()`
  - Task lists display with `format_task_list_table()`
  - Schedules display with `format_schedule_table()`
  - Status messages enhanced with emojis
  - Summary statistics displayed with `format_summary_stats()`

- **`requirements.txt`** — Added dependency
  - Added `tabulate>=0.9.0` for table formatting

- **`README.md`** — Documentation
  - New "🎨 User-Friendly Output Formatting" section
  - Function reference for all formatting utilities
  - Examples showing before/after formatting
  - Library usage documentation

## Integration with Streamlit

The formatting utilities integrate seamlessly with Streamlit:
1. **Tables displayed via `st.code()`** — preserves ASCII table formatting and colors
2. **Emojis render natively** — Streamlit supports all Unicode emojis
3. **Color codes work in code blocks** — ANSI color codes render correctly in `st.code()`
4. **Responsive design** — tables adapt to content length

## Usage Examples

### Display a Task List
```python
from formatting_utils import format_task_list_table

task_data = [
    {
        "status": "pending",
        "pet": "Mochi",
        "species": "dog",
        "title": "Morning walk",
        "duration": 30,
        "priority": "high",
        "time_window": "07:00—09:00"
    }
]

table = format_task_list_table(task_data)
st.code(table, language=None)  # Display in Streamlit
```

### Display Schedule
```python
from formatting_utils import format_schedule_table

schedule_data = [
    {
        "time": "07:00—07:30",
        "task": "Morning walk",
        "pet": "Mochi",
        "species": "dog",
        "duration": 30,
        "priority": "HIGH"
    }
]

table = format_schedule_table(schedule_data)
st.code(table, language=None)
```

### Display Pet Summary
```python
from formatting_utils import format_pet_summary_table

pet_data = [
    {"name": "Mochi", "species": "dog", "task_count": 5},
    {"name": "Whiskers", "species": "cat", "task_count": 3}
]

table = format_pet_summary_table(pet_data)
st.code(table, language=None)
```

## Extensibility

The formatting utilities are designed for easy extension:

1. **Add new task type emoji**: Add entry to `TASK_EMOJIS` dict
2. **Add new pet species emoji**: Add entry to `SPECIES_EMOJIS` dict
3. **Add new status type**: Add entry to `STATUS_EMOJIS` dict
4. **Custom color schemes**: Modify `PRIORITY_COLORS` mapping
5. **Different table formats**: Update `tablefmt` parameter in tabulate calls

## Testing

All formatting utilities tested and verified to:
- ✅ Generate proper emoji output
- ✅ Apply color codes correctly
- ✅ Create well-formatted ASCII tables
- ✅ Handle missing data gracefully
- ✅ Work seamlessly with Streamlit

## Dependencies

- **tabulate** (v0.9.0+) — ASCII table generation
  - Provides multiple table formats
  - Handles column alignment
  - Creates professional-looking output

## Performance

- Minimal overhead (table generation is fast)
- Emoji lookup is O(1) via dictionary
- Color codes are pre-defined constants
- No external API calls

## Accessibility

- Text-based emoji alternatives available
- Color not the only way to convey information
- Table headers with descriptive emoji prefixes
- High contrast colors for visibility
