# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core actions identified:**
1. **Enter pet and owner information** – User provides owner name, pet name/species, and preferences
2. **Manage care tasks** – User adds/edits tasks with title, duration (minutes), and priority level
3. **Generate and view daily schedule** – System produces an ordered plan based on time available and task priorities

**Classes and responsibilities:**
- **Owner**: Holds owner name, available hours per day, and preferences. Provides methods to retrieve available hours and update preferences. Serves as the constraint provider for scheduling (how much time is available).
- **Pet**: Represents the pet with name, species, and owner reference. Provides methods to get owner info and display formatted pet info. Links pets to their owners in the system.
- **Task**: Represents a care activity (walk, feeding, medication, etc.) with title, duration in minutes, priority level (low/medium/high), and recurrence pattern (daily/weekly/one-time). Provides methods to retrieve duration and priority. Acts as the basic unit of scheduling work.
- **Scheduler**: The core scheduling engine that takes an Owner, Pet, and list of Tasks. Produces a DailySchedule by sorting tasks by priority and fitting them within available time constraints. Responsible for all scheduling logic and decision-making.
- **DailySchedule**: Represents the output—a specific day's plan containing ScheduledTask objects with actual times. Provides methods to display the formatted schedule and explain the reasoning behind task inclusion/exclusion.
- **ScheduledTask**: Wraps a Task with specific timing information (start_time, end_time, explanation). Acts as the final scheduled unit that appears in the daily plan.

**b. Design changes**

During the skeleton review, the following design improvements were made to address missing relationships and potential logic bottlenecks:

1. **Added `pet: Pet` to Task (with owner reference)**
   - **Why**: Tasks need to know which pet they serve. Without this, the system can't handle multi-pet scenarios or validate which tasks apply to which animal.
   - **Impact**: Enables filtering tasks by pet and clearer ownership semantics.

2. **Added `owner: Owner` to DailySchedule**
   - **Why**: The schedule needs to reference the owner executing it. Without this, `explain_reasoning()` can't validate against owner availability constraints or explain why tasks were dropped due to owner limitations.
   - **Impact**: Enables full validation and meaningful explanations of scheduling decisions.

3. **Added `date` parameter to `Scheduler.generate_schedule(target_date: date)`**
   - **Why**: The scheduler needs to know which date it's planning for. Without this, multi-day planning and recurring task expansion are impossible.
   - **Impact**: Allows generating schedules for any date and laying groundwork for recurring task handling.

4. **Added `dropped_tasks: List[Task]` to DailySchedule**
   - **Why**: The system needs to track which tasks were excluded and why. Without this, `explain_reasoning()` can't explain the full reasoning (what was included AND what was excluded).
   - **Impact**: Enables complete transparency about scheduling trade-offs.

5. **Changed `fit_tasks_in_time()` return type to `tuple (scheduled_tasks, dropped_tasks)`**
   - **Why**: Instead of returning only scheduled tasks, the method now returns both scheduled and dropped. This preserves the data needed for `explain_reasoning()` and makes trade-offs explicit.
   - **Impact**: The scheduling logic can now report complete results with full traceability.

6. **Added `preferred_time_window: Optional[tuple]` to Task**
   - **Why**: Some tasks (medication, feeding) have time-of-day constraints. A simple duration model can't capture this, leading to unrealistic schedules.
   - **Impact**: Enables time-aware scheduling where appropriate tasks appear at the right times.

7. **Added `status: str` to ScheduledTask (scheduled, completed, skipped, rescheduled)**
   - **Why**: Tasks need lifecycle tracking. Without this, the system can't distinguish between a planned but not-yet-executed task and one that was actually completed or skipped.
   - **Impact**: Enables tracking task execution and rescheduling capabilities for future iterations.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
