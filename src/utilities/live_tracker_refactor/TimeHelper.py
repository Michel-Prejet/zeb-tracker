from datetime import timedelta, time, datetime

from utilities.live_tracker_refactor.winnipeg_transit_api.exceptions.InvalidAPIStopTimeError import \
    InvalidAPIStopTimeError
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.exceptions.TransitGTFSError import InvalidDepartureTimeError


OVERLAP_START_TIME = time(0, 0, 0)
OVERLAP_END_TIME = time(3, 30, 0)
HOURS_PER_DAY = 24
NUM_TOKENS = 3
MAX_NUM_MINUTES = 60
MAX_NUM_SECONDS = 60

def parse_api_time(raw_datetime: str, err_msg="") -> timedelta:
    """
    Creates a timedelta object from an ISO datetime string retrieved from the
    Winnipeg Transit API. 12 am, 1 am, 2 am, and 3 am are represented as hours
    24, 25, 26, and 27, respectively. If the string is not a valid ISO datetime,
    an InvalidAPIStopTimeError is raised.

    :param raw_datetime: the ISO datetime string to parse.
    :param err_msg: the error message to pass to the exception if an error
    occurs.
    :return: a timedelta object created from the given string.
    """
    if "T" not in raw_datetime:
        raise InvalidAPIStopTimeError(err_msg)

    raw_time = raw_datetime.split("T")[1]
    time_tokens = raw_time.split(":")

    if len(time_tokens) != NUM_TOKENS:
        raise InvalidAPIStopTimeError(err_msg)
    for token in time_tokens:
        if not token.isdigit():
            raise InvalidAPIStopTimeError(err_msg)

    hours, minutes, seconds = map(int, time_tokens)
    try:
        parsed_time = time(hours, minutes, seconds)
    except ValueError:
        raise InvalidAPIStopTimeError(err_msg)

    if OVERLAP_START_TIME <= parsed_time <= OVERLAP_END_TIME:
        hours += HOURS_PER_DAY

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def parse_gtfs_time(raw_time: str, err_msg="") -> timedelta:
    """
    Creates a timedelta object from a raw string. If the string is not
    of the form HH:MM:SS, an InvalidDepartureTimeError is raised.

    :param raw_time: the raw string to convert to a timedelta object.
    :param err_msg: the error message to pass to the exception if an error
    occurs.
    :return: a timedelta object created from the given string.
    """

    tokens = raw_time.split(":")
    if len(tokens) != NUM_TOKENS:
        raise InvalidDepartureTimeError(err_msg)
    for val in tokens:
        if not val.isdigit():
            raise InvalidDepartureTimeError(err_msg)

    hours, minutes, seconds = map(int, tokens)

    if minutes >= MAX_NUM_MINUTES or seconds >= MAX_NUM_SECONDS:
        raise InvalidDepartureTimeError(err_msg)

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