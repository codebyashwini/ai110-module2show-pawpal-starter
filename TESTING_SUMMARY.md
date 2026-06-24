# PawPal+ Test Suite Summary

## Overview
The test suite in `tests/test_pawpal.py` covers **13 comprehensive tests** across 5 test classes, focusing on core system behaviors.

---

## Test Classes & Coverage

### 1. **TestTaskCompletion** (1 test)
**Purpose:** Verify task completion tracking
- `test_mark_complete_changes_status` — Confirms `task.mark_complete()` sets `completed = True`

---

### 2. **TestTaskAddition** (1 test)
**Purpose:** Verify tasks are properly added to pets
- `test_adding_task_increases_pet_task_count` — Confirms pet task list grows when tasks are added

---

### 3. **TestSortingCorrectness** (3 tests)
**Purpose:** Verify `Scheduler.sort_tasks_by_time()` works correctly

#### Test Cases:
1. **`test_sort_tasks_chronological_order`**
   - Creates 3 tasks OUT OF ORDER: evening (18:00), morning (07:00), afternoon (15:00)
   - Verifies sorted order: morning → afternoon → evening
   - **Key assertion:** `assert sorted_tasks[0].title == "Morning walk"`

2. **`test_sort_tasks_without_time_window_appear_last`**
   - Creates 1 task with time window, 1 without
   - Verifies timed task comes first, no-window task comes last
   - **Key insight:** Tasks without `preferred_time_window` return `float('inf')` in sort key, pushing them to the end

3. **`test_sort_empty_task_list`**
   - Verifies sorting an empty list returns empty list (edge case)
   - **Key assertion:** `assert sorted_tasks == []`

---

### 4. **TestRecurrenceLogic** (4 tests)
**Purpose:** Verify recurring task creation via `Scheduler.mark_task_complete()`

#### Test Cases:
1. **`test_daily_task_creates_next_occurrence`**
   - Creates a daily task with today's due date
   - Marks it complete
   - Verifies:
     - Original task is marked `completed = True`
     - New task is created for tomorrow
     - Pet now has 2 tasks
   - **Key code:** `next_task.due_date == today + timedelta(days=1)`

2. **`test_weekly_task_creates_next_occurrence`**
   - Similar to daily, but verifies 7-day gap
   - **Key code:** `next_task.due_date == today + timedelta(weeks=1)`

3. **`test_one_time_task_does_not_create_next_occurrence`**
   - Marks a `recurring="one-time"` task complete
   - Verifies `mark_task_complete()` returns `None`
   - Verifies pet still has only 1 task
   - **Key assertion:** `assert next_task is None`

4. **`test_recurring_task_without_due_date_does_not_create_next`**
   - Tests edge case: recurring task with no `due_date`
   - Verifies no next task is created (can't calculate next date)
   - **Key insight:** The method checks `if not task.due_date: return None`

---

### 5. **TestConflictDetection** (4 tests)
**Purpose:** Verify `Scheduler.detect_time_conflicts()` flags overlapping time windows

#### Test Cases:
1. **`test_detect_overlapping_time_windows`**
   - Creates 2 tasks with overlapping times: 15:00-16:00 and 15:30-16:30
   - Verifies conflict is detected
   - **Key assertion:** `assert len(conflicts) > 0`
   - **Important setup:** Must call `owner.add_pet()` to register pets!

2. **`test_no_conflict_non_overlapping_windows`**
   - Tasks at 08:00-09:00 and 10:00-11:00 (no overlap)
   - Verifies no conflict
   - **Key assertion:** `assert len(conflicts) == 0`

3. **`test_no_conflict_when_task_lacks_time_window`**
   - 1 task with time window, 1 without
   - Verifies no conflict (can't compare if one has no window)
   - **Key insight:** `_tasks_have_conflicting_times()` checks both tasks have windows

4. **`test_conflict_at_exact_boundary`**
   - Tasks touching exactly: 09:00-10:00 and 10:00-11:00
   - Verifies they DON'T conflict (touching is OK)
   - **Key code:** Overlap uses `<` (not `<=`): `start1_min < end2_min and start2_min < end1_min`
   - **Why?** 10:00 (end of task1) is NOT less than 10:00 (start of task2), so no overlap

---

## Key Testing Patterns Used

### 1. **Happy Path vs. Edge Cases**
- Each test class covers both normal scenarios and edge cases (empty lists, missing fields, boundary conditions)

### 2. **Setup Fixtures**
- Each test creates its own `Owner`, `Pet(s)`, and `Task(s)`
- **Critical step:** Must call `owner.add_pet()` to register pets (learned from debugging!)

### 3. **Assertion Clarity**
- Each assertion is explicit: `assert X`, not just `assert X is not None`
- Comments explain what's being tested

### 4. **Dataclass & Property Testing**
- Tests verify both object creation and property changes
- Example: confirming `task.completed` flips from `False` to `True`

---

## Common Bugs Found & Fixed

### Bug #1: Missing `owner.add_pet()`
**Symptom:** Conflict detection tests returned 0 conflicts even with overlaps
**Root Cause:** Pets were created but not registered to the owner
**Fix:** Added `owner.add_pet(pet1)` and `owner.add_pet(pet2)` in test setup

**Lesson:** `owner.get_all_tasks()` iterates through `owner.pets`, so pets must be registered!

---

## Running the Tests

```bash
# Run all tests
pytest tests/test_pawpal.py -v

# Run a specific test class
pytest tests/test_pawpal.py::TestSortingCorrectness -v

# Run a single test
pytest tests/test_pawpal.py::TestSortingCorrectness::test_sort_tasks_chronological_order -v
```

---

## Coverage Summary

| Behavior | Tests | Status |
|----------|-------|--------|
| Task Completion | 1 | ✅ PASS |
| Task Addition | 1 | ✅ PASS |
| Sorting by Time | 3 | ✅ PASS |
| Recurrence Logic | 4 | ✅ PASS |
| Conflict Detection | 4 | ✅ PASS |
| **TOTAL** | **13** | **✅ ALL PASS** |

---

## Next Steps

Possible additional tests to consider:
- `filter_tasks_by_status()` — pending vs completed filtering
- `filter_tasks_by_pet()` — pet-specific task filtering
- `fit_tasks_in_time()` — greedy scheduling within time constraints
- `generate_schedule()` — end-to-end schedule generation
