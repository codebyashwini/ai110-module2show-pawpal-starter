import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, DailySchedule, ScheduledTask

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ interactive demo.

Use this app to create pets, add care tasks, and generate daily schedules.
"""
)

# Initialize owner in session state (maintains state across Streamlit reruns)
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_hours_per_day=4)

owner = st.session_state.owner

st.divider()

st.subheader("👤 Owner & Pet Setup")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_hours_per_day = st.number_input(
        "Available hours per day", min_value=1, max_value=24, value=owner.available_hours_per_day
    )

st.markdown("### Add a Pet")
st.caption("Create a new pet and add it to your care plan.")

col1, col2 = st.columns(2)
with col1:
    new_pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"], key="species_input")

if st.button("Add pet"):
    new_pet = Pet(name=new_pet_name, species=new_pet_species, owner=owner)
    owner.add_pet(new_pet)
    st.success(f"✓ Added {new_pet_name} ({new_pet_species}) to your pets!")
    st.rerun()

if owner.pets:
    st.write("**Your pets:**")
    pet_list = [f"{pet.display_info()}" for pet in owner.pets]
    st.table({"Pet": pet_list})
else:
    st.info("No pets yet. Add one above!")

st.divider()

st.subheader("📋 Tasks")
st.caption("Add care tasks for each pet.")

if owner.pets:
    selected_pet_name = st.selectbox("Select pet for task", [p.name for p in owner.pets])
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30, key="duration_input")
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority_input")

    if st.button("Add task"):
        new_task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
        selected_pet.add_task(new_task)
        st.success(f"✓ Added task '{task_title}' to {selected_pet_name}!")
        st.rerun()

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.markdown("### All Tasks")

        # Filter and display options
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.radio("Filter by status:", ["All", "Pending", "Completed"], horizontal=True)
        with col2:
            sort_option = st.radio("Sort by:", ["Priority (high→low)", "Time window (early→late)"], horizontal=True)

        # Build the task list based on filters
        scheduler = Scheduler(owner)

        # Apply status filter
        if filter_status == "Completed":
            display_tasks = scheduler.filter_tasks_by_status(all_tasks, status="completed")
        elif filter_status == "Pending":
            display_tasks = scheduler.filter_tasks_by_status(all_tasks, status="pending")
        else:
            display_tasks = all_tasks

        # Apply sorting
        if sort_option == "Time window (early→late)":
            display_tasks = scheduler.sort_tasks_by_time(display_tasks)
        else:  # Default: sort by priority
            display_tasks = scheduler.sort_tasks_by_priority(display_tasks)

        # Conflict detection
        conflicts = scheduler.detect_time_conflicts(all_tasks)
        if conflicts:
            st.warning("⚠️ **Time Conflicts Detected!**")
            for conflict in conflicts:
                st.write(conflict)
            st.caption("These tasks have overlapping preferred time windows. Consider rescheduling one of them to avoid conflicts.")
        else:
            st.success("✓ No time conflicts detected!")

        # Display tasks in professional table
        if display_tasks:
            task_data = []
            for task in display_tasks:
                status_indicator = "✓ Done" if task.completed else "○ Pending"
                time_window = f"{task.preferred_time_window[0]}–{task.preferred_time_window[1]}" if task.preferred_time_window else "No time set"

                task_data.append({
                    "Status": status_indicator,
                    "Pet": task.pet.name if task.pet else "Unknown",
                    "Task": task.title,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority.capitalize(),
                    "Time Window": time_window,
                    "Recurring": task.recurring.capitalize()
                })
            st.table(task_data)
        else:
            st.info("No tasks match your filters.")
    else:
        st.info("No tasks yet. Add one above!")
else:
    st.info("Add a pet first to start creating tasks.")

st.divider()

st.subheader("📅 Generate Schedule")
st.caption("Create a daily schedule based on available time and task priorities.")

if st.button("Generate schedule for today", type="primary"):
    if not owner.pets:
        st.error("❌ Please add at least one pet first.")
    elif not owner.get_all_tasks():
        st.error("❌ Please add at least one task first.")
    else:
        scheduler = Scheduler(owner)
        daily_schedule = scheduler.generate_schedule(date.today())

        # Show today's schedule in a nice format
        st.markdown("### 📌 Today's Schedule")

        if daily_schedule.scheduled_tasks:
            schedule_data = []
            for scheduled_task in daily_schedule.scheduled_tasks:
                task = scheduled_task.task
                schedule_data.append({
                    "Time": scheduled_task.format_time(),
                    "Task": task.title,
                    "Pet": task.pet.name if task.pet else "Unknown",
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority.capitalize()
                })
            st.table(schedule_data)
            st.success(f"✓ Scheduled {len(daily_schedule.scheduled_tasks)} task(s) for today")
        else:
            st.info("No tasks scheduled for today.")

        # Show dropped tasks with warning if any
        if daily_schedule.dropped_tasks:
            st.warning("⚠️ **Could Not Fit All Tasks**")
            st.caption(f"The following {len(daily_schedule.dropped_tasks)} task(s) don't fit in your available time. Consider scheduling them for another day:")

            dropped_data = []
            for task in daily_schedule.dropped_tasks:
                dropped_data.append({
                    "Task": task.title,
                    "Pet": task.pet.name if task.pet else "Unknown",
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority.capitalize()
                })
            st.table(dropped_data)
        else:
            st.success("✓ All tasks fit in your available time!")

        # Show detailed reasoning in an expander
        with st.expander("📊 View detailed reasoning"):
            st.markdown("### Scheduling Logic")
            reasoning_text = daily_schedule.explain_reasoning()
            st.text(reasoning_text)
