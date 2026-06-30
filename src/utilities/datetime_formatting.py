from datetime import date, timedelta, datetime
from constants.app_constants import SECONDS_PER_HOUR, MINUTES_PER_HOUR, LAST_DATE_SEEN_UNKNOWN_PLACEHOLDER
from domain.bus import Bus
from utilities.invariant_helper import require_not_none, require_state


def format_datetime(d: datetime) -> str:
    """
    Creates a string in YYYY-MM-DD HH:MM:SS format from a datetime object.

    :param d: the datetime object to format as a string.
    :return: a string of the form YYYY-MM-DD HH:MM:SS.
    """
    require_not_none(d, "Datetime object should not be None.")

    return d.strftime('%Y-%m-%d %H:%M:%S')

def format_date(d: date) -> str:
    """
    Creates a string in MONTH DAY, YEAR format from a date object.

    :param d: the date object to format as a string.
    :return: a string of the form MONTH DAY, YEAR.
    """
    require_not_none(d, "Date object should not be None.")

    return f"{d.strftime('%B')} {d.day}, {d.year}"

def format_timedelta(td: timedelta) -> str:
    """
    Creates a string in HH:MM:SS format from a timedelta object.

    :param td: the timedelta object to convert to a string.
    :return: a string representing the given timedelta object in HH:MM:SS format.
    """
    require_not_none(td, "Timedelta object should not be None.")
    require_state(td >= timedelta(),
                  "Cannot format negative Timedelta object.")

    total_seconds = int(td.total_seconds())
    hours = total_seconds // SECONDS_PER_HOUR
    minutes = (total_seconds % SECONDS_PER_HOUR) // MINUTES_PER_HOUR
    seconds = total_seconds % MINUTES_PER_HOUR

    return f"{hours:02}:{minutes:02}:{seconds:02}"

def format_last_run_date(bus: Bus) -> str:
    """
    :bus: the bus for which to get the last run date as a string.
    :return: the last run completed by the given bus as a string of the form
    MONTH DAY, YEAR (e.g. May 2, 2026) or "never" if the given bus hasn't
    completed any runs.
    """
    require_not_none(bus, "Bus should not be None.")

    last_run = bus.last_run()

    if last_run is None:
        return LAST_DATE_SEEN_UNKNOWN_PLACEHOLDER
    return format_date(last_run.run_date)