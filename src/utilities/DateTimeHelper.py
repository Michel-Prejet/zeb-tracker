from datetime import date, timedelta


SECONDS_PER_HOUR = 3600
MINUTES_PER_HOUR = 60

def format_date(d: date) -> str:
    """
    Creates a string in MONTH DAY, YEAR format from a date object.

    :param d: the date object to format as a string.
    :return: a string of the form MONTH DAY, YEAR.
    """
    return f"{d.strftime('%B')} {d.day}, {d.year}"

def _format_timedelta(td: timedelta) -> str:
    """
    Creates a string in HH:MM:SS format from a timedelta object.

    :param td: the timedelta object to convert to a string.
    :return: a string representing the given timedelta object in HH:MM:SS format.
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // SECONDS_PER_HOUR
    minutes = (total_seconds % SECONDS_PER_HOUR) // MINUTES_PER_HOUR
    seconds = total_seconds % MINUTES_PER_HOUR

    return f"{hours:02}:{minutes:02}:{seconds:02}"