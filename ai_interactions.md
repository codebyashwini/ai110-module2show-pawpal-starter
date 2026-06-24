# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a third algorithmic capability (beyond the basic requirements) that demonstrates advanced scheduling logic. Specifically: implement a "Next Available Slot" algorithm that finds conflict-free time windows for tasks, along with comprehensive tests.

**What did the agent do?**

1. **Modified [pawpal_system.py](pawpal_system.py:296-354)** — Added the `find_next_available_slot()` method to the Scheduler class:
   - Scans the day in 15-minute intervals from 7:00 AM to 11:00 PM
   - Checks for conflicts against existing task time windows
   - Returns the first available (start_time, end_time) tuple or None if task cannot fit
   - Includes comprehensive docstring explaining the algorithm and use cases

2. **Extended [tests/test_pawpal.py](tests/test_pawpal.py:396-502)** — Added TestNextAvailableSlot class with 5 new tests:
   - `test_find_slot_with_no_existing_tasks` — Verifies earliest slot at 7:00 AM when no conflicts exist
   - `test_find_slot_avoids_existing_conflict` — Confirms algorithm skips blocked time windows
   - `test_find_slot_with_multiple_conflicts` — Tests navigation through multiple blockers
   - `test_find_slot_returns_none_when_no_space` — Validates None return when task too long
   - `test_find_slot_respects_day_boundary` — Ensures scheduling stops before 11:00 PM

3. **Updated [README.md](README.md:171)** — Added entry to the Features table documenting the new algorithm with its method name, description, and practical use cases.

**What did you have to verify or fix manually?**

Fixed one test assertion:
- Initial `test_find_slot_returns_none_when_no_space` test used an 800-minute task, which actually fits within the 7:00 AM–11:00 PM window (960 minutes available)
- Changed task duration to 1000 minutes to properly test the boundary condition where a task cannot fit
- All 18 tests (13 original + 5 new) now pass successfully

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
