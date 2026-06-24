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
        st.write("**All tasks:**")
        task_data = []
        for task in all_tasks:
            task_data.append({
                "Pet": task.pet.name if task.pet else "Unknown",
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Recurring": task.recurring
            })
        st.table(task_data)
    else:
        st.info("No tasks yet. Add one above!")
else:
    st.info("Add a pet first to start creating tasks.")

st.divider()

st.subheader("📅 Generate Schedule")
st.caption("Create a daily schedule based on available time and task priorities.")

if st.button("Generate schedule for today"):
    if not owner.pets:
        st.error("Please add at least one pet first.")
    elif not owner.get_all_tasks():
        st.error("Please add at least one task first.")
    else:
        scheduler = Scheduler(owner)
        daily_schedule = scheduler.generate_schedule(date.today())

        st.markdown("### Today's Schedule")
        st.info(daily_schedule.display_plan())

        st.markdown("### Scheduling Reasoning")
        st.write(daily_schedule.explain_reasoning())
