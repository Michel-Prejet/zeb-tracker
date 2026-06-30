from datetime import timedelta, time, datetime
from constants.app_constants import HOURS_PER_DAY, SECONDS_PER_MINUTE, MINUTES_PER_HOUR
from utilities.live_tracker.winnipeg_transit_api.exceptions.transit_api_error import InvalidStopTimeError
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.transit_gtfs_error import MalformedTokenError


OVERLAP_START_TIME = time(0, 0, 0)
OVERLAP_END_TIME = time(3, 30, 0)
NUM_TOKENS_IN_GTFS_TIME = 3

def parse_api_time(raw_datetime: str) -> timedelta:
    """
    Creates a timedelta object from an ISO datetime string retrieved from the
    Winnipeg Transit API. 12 am, 1 am, 2 am, and 3 am are represented as hours
    24, 25, 26, and 27, respectively. If the string is not a valid ISO datetime,
    an InvalidAPIStopTimeError is raised.

    :param raw_datetime: the ISO datetime string to parse.
    :return: a timedelta object created from the given string.
    """
    if "T" not in raw_datetime:
        raise InvalidStopTimeError(raw_datetime)

    raw_time = raw_datetime.split("T")[1]
    time_tokens = raw_time.split(":")

    if len(time_tokens) != NUM_TOKENS_IN_GTFS_TIME:
        raise InvalidStopTimeError(raw_datetime)
    for token in time_tokens:
        if not token.isdigit():
            raise InvalidStopTimeError(raw_datetime)

    hours, minutes, seconds = map(int, time_tokens)
    try:
        parsed_time = time(hours, minutes, seconds)
    except ValueError:
        raise InvalidStopTimeError(raw_datetime)

    if OVERLAP_START_TIME <= parsed_time <= OVERLAP_END_TIME:
        hours += HOURS_PER_DAY

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def parse_gtfs_time(raw_time: str, filename: str, row: int) -> timedelta:
    """
    Creates a timedelta object from a raw string. If the string is not
    of the form HH:MM:SS, an InvalidDepartureTimeError is raised.

    :param raw_time: the raw string to convert to a timedelta object.
    :param filename: the name of the file in which the time was read.
    :param row: the row in which the time was read.
    :return: a timedelta object created from the given string.
    """

    tokens = raw_time.split(":")
    if len(tokens) != NUM_TOKENS_IN_GTFS_TIME:
        raise MalformedTokenError(filename, row)
    for val in tokens:
        if not val.isdigit():
            raise MalformedTokenError(filename, row)

    hours, minutes, seconds = map(int, tokens)

    if minutes >= MINUTES_PER_HOUR or seconds >= SECONDS_PER_MINUTE:
        raise MalformedTokenError(filename, row)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def get_curr_time_as_timedelta() -> timedelta:
    """
    :return: the current time as a timedelta object, where 12 am, 1 am, 2 am,
    and 3 am are represented as hours 24, 25, 26, and 27, respectively.
    """
    curr_datetime = datetime.now()

    hours, minutes, seconds = int(curr_datetime.hour), int(curr_datetime.minute), int(curr_datetime.second)

    if OVERLAP_START_TIME <= curr_datetime.time() <= OVERLAP_END_TIME:
        hours += HOURS_PER_DAY

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)