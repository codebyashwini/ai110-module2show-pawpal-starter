"""
Formatting utilities for PawPal+ user interface.
Provides color-coded indicators, emojis, and structured table formatting.
"""

from typing import List, Dict, Any
from tabulate import tabulate


# Task type emoji mappings
TASK_EMOJIS = {
    "walk": "🚶",
    "feed": "🍽️",
    "play": "🎾",
    "groom": "✂️",
    "vet": "💊",
    "sleep": "😴",
    "bath": "🚿",
    "train": "🎓",
    "exercise": "💪",
    "cuddle": "🤗",
}

# Priority color codes (ANSI)
PRIORITY_COLORS = {
    "high": "\033[91m",      # Bright red
    "medium": "\033[93m",    # Bright yellow
    "low": "\033[92m",       # Bright green
}

# Status emojis
STATUS_EMOJIS = {
    "completed": "✅",
    "pending": "⏳",
    "scheduled": "📌",
    "skipped": "⏭️",
    "rescheduled": "🔄",
}

# Species emojis
SPECIES_EMOJIS = {
    "dog": "🐕",
    "cat": "🐈",
    "rabbit": "🐰",
    "bird": "🦜",
    "hamster": "🐹",
    "fish": "🐠",
    "turtle": "🐢",
    "guinea pig": "🐹",
    "other": "🐾",
}

RESET_COLOR = "\033[0m"


def get_task_emoji(task_title: str) -> str:
    """Returns an emoji based on task title keywords."""
    task_lower = task_title.lower()
    for keyword, emoji in TASK_EMOJIS.items():
        if keyword in task_lower:
            return emoji
    return "📝"


def get_species_emoji(species: str) -> str:
    """Returns an emoji for the given pet species."""
    return SPECIES_EMOJIS.get(species.lower(), "🐾")


def format_priority_indicator(priority: str) -> str:
    """Returns a colored priority indicator with emoji."""
    indicators = {
        "high": "🔴 HIGH",
        "medium": "🟡 MEDIUM",
        "low": "🟢 LOW",
    }
    emoji_text = indicators.get(priority, "❓ UNKNOWN")
    color = PRIORITY_COLORS.get(priority, "")
    return f"{color}{emoji_text}{RESET_COLOR}"


def format_status_badge(status: str) -> str:
    """Returns a formatted status badge with emoji."""
    emoji = STATUS_EMOJIS.get(status, "❓")
    status_text = status.upper()
    return f"{emoji} {status_text}"


def format_colored_priority(priority: str) -> str:
    """Returns priority text with color formatting."""
    color = PRIORITY_COLORS.get(priority, "")
    return f"{color}{priority.upper()}{RESET_COLOR}"


def format_task_list_table(tasks: List[Dict[str, Any]], use_color: bool = True) -> str:
    """
    Formats a list of task dictionaries as a structured table.

    Args:
        tasks: List of task dictionaries with keys like 'title', 'duration', 'priority', etc.
        use_color: Whether to apply color formatting

    Returns:
        Formatted table string
    """
    if not tasks:
        return "No tasks to display."

    table_data = []
    for task in tasks:
        row = []

        # Status with emoji
        status = task.get('status', 'pending').lower()
        row.append(format_status_badge(status))

        # Pet name with emoji
        pet_name = task.get('pet', 'Unknown')
        species = task.get('species', 'other')
        emoji = get_species_emoji(species)
        row.append(f"{emoji} {pet_name}")

        # Task title with task emoji
        title = task.get('title', 'Untitled')
        task_emoji = get_task_emoji(title)
        row.append(f"{task_emoji} {title}")

        # Duration
        duration = task.get('duration', 0)
        row.append(f"{duration} min")

        # Priority with color
        priority = task.get('priority', 'medium').lower()
        if use_color:
            row.append(format_priority_indicator(priority))
        else:
            row.append(priority.upper())

        # Time window
        time_window = task.get('time_window', 'Flexible')
        row.append(time_window)

        table_data.append(row)

    headers = ["Status", "Pet", "Task", "Duration", "Priority", "Time Window"]
    return tabulate(table_data, headers=headers, tablefmt="grid")


def format_schedule_table(scheduled_tasks: List[Dict[str, Any]]) -> str:
    """
    Formats a schedule with time slots as a structured table.

    Args:
        scheduled_tasks: List of scheduled task dicts with 'time', 'task', 'pet', etc.

    Returns:
        Formatted schedule table string
    """
    if not scheduled_tasks:
        return "No scheduled tasks."

    table_data = []
    for st in scheduled_tasks:
        time_slot = st.get('time', '--:-- — --:--')
        task_emoji = get_task_emoji(st.get('task', ''))
        task_name = f"{task_emoji} {st.get('task', 'Untitled')}"
        pet_emoji = get_species_emoji(st.get('species', 'other'))
        pet_name = f"{pet_emoji} {st.get('pet', 'Unknown')}"
        duration = f"{st.get('duration', 0)} min"
        priority = st.get('priority', 'medium').upper()

        table_data.append([time_slot, task_name, pet_name, duration, priority])

    headers = ["⏰ Time", "📝 Task", "🐾 Pet", "⏱️ Duration", "⭐ Priority"]
    return tabulate(table_data, headers=headers, tablefmt="fancy_grid")


def format_pet_summary_table(pets: List[Dict[str, Any]]) -> str:
    """
    Formats a list of pets with their task counts as a table.

    Args:
        pets: List of pet dicts with 'name', 'species', 'task_count', etc.

    Returns:
        Formatted pet summary table string
    """
    if not pets:
        return "No pets added yet."

    table_data = []
    for pet in pets:
        name = pet.get('name', 'Unknown')
        species = pet.get('species', 'other')
        species_emoji = get_species_emoji(species)
        task_count = pet.get('task_count', 0)

        # Create a visual task count indicator
        task_indicator = f"📋 {task_count} task{'s' if task_count != 1 else ''}"

        table_data.append([
            f"{species_emoji} {name}",
            species.capitalize(),
            task_indicator,
        ])

    headers = ["🐾 Pet", "Species", "Tasks"]
    return tabulate(table_data, headers=headers, tablefmt="rounded_grid")


def format_summary_stats(total_tasks: int, completed_tasks: int, dropped_tasks: int,
                        used_minutes: int, available_minutes: int) -> str:
    """
    Formats summary statistics with visual indicators.

    Returns:
        Formatted summary string
    """
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    utilization_rate = (used_minutes / available_minutes * 100) if available_minutes > 0 else 0

    lines = [
        "=" * 50,
        "📊 SCHEDULE SUMMARY",
        "=" * 50,
        f"✅ Completed:      {completed_tasks}/{total_tasks} ({completion_rate:.1f}%)",
        f"⏳ Pending:        {total_tasks - completed_tasks}",
        f"⏭️  Dropped:        {dropped_tasks}",
        "-" * 50,
        f"⏱️  Time Used:       {used_minutes}/{available_minutes} minutes ({utilization_rate:.1f}%)",
        f"🕐 Time Remaining: {max(0, available_minutes - used_minutes)} minutes",
        "=" * 50,
    ]

    return "\n".join(lines)


def format_conflict_warning(task1_title: str, task1_pet: str, task1_window: tuple,
                           task2_title: str, task2_pet: str, task2_window: tuple) -> str:
    """
    Formats a time conflict warning with emojis and structure.

    Returns:
        Formatted warning string
    """
    emoji1 = get_task_emoji(task1_title)
    emoji2 = get_task_emoji(task2_title)

    start1, end1 = task1_window
    start2, end2 = task2_window

    return (
        f"\n⚠️  TIME CONFLICT DETECTED\n"
        f"  {emoji1} '{task1_title}' ({task1_pet})\n"
        f"     ⏰ {start1}—{end1}\n"
        f"  {emoji2} '{task2_title}' ({task2_pet})\n"
        f"     ⏰ {start2}—{end2}\n"
    )


def format_success_message(message: str) -> str:
    """Formats a success message with emoji."""
    return f"✅ {message}"


def format_warning_message(message: str) -> str:
    """Formats a warning message with emoji."""
    return f"⚠️  {message}"


def format_info_message(message: str) -> str:
    """Formats an info message with emoji."""
    return f"ℹ️  {message}"


def format_error_message(message: str) -> str:
    """Formats an error message with emoji."""
    return f"❌ {message}"
