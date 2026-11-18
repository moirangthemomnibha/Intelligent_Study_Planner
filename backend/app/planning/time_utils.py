"""Time conversion and formatting utilities."""


def minutes_to_hours(minutes):
    """Convert minutes into hours."""
    return minutes / 60.0


def hours_to_minutes(hours):
    """Convert hours into minutes."""
    return round(float(hours) * 60)


def format_duration(hours):
    """Format hours into readable hours and minutes."""

    total_minutes = round(float(hours) * 60)

    whole_hours, remaining_minutes = divmod(total_minutes, 60)

    if whole_hours and remaining_minutes:
        return f"{whole_hours}h {remaining_minutes}m"

    if whole_hours:
        return f"{whole_hours}h"

    return f"{remaining_minutes}m"


def fmt(hours):
    """Short duration formatting alias."""
    return format_duration(hours)