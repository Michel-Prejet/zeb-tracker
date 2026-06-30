from constants.app_constants import MIN_BUS_TRACKING_NUM, MAX_BUS_TRACKING_NUM, MIN_BUS_YEAR
from domain.bus import Bus
from domain.validation.exceptions.bus_error import InvalidTrackingNumberError, InvalidYearError, EmptyModelError
from utilities.invariant_helper import require_not_none


def validate_tracking_number(raw: str) -> int:
    """"
    Validates a given tracking number and raises an exception if it is invalid.
    To be valid, a tracking number must contain exactly three digits. Removes
    all leading and trailing whitespace before validation.

    :param raw: the tracking number to validate.
    :return: the validated tracking number, with all leading/trailing
    whitespace removed.
    """
    require_not_none(raw, "Tracking number should not be None.")

    raw = raw.strip()

    try:
        tracking_num = int(raw)
    except ValueError:
        raise InvalidTrackingNumberError()

    if tracking_num < MIN_BUS_TRACKING_NUM or tracking_num > MAX_BUS_TRACKING_NUM:
        raise InvalidTrackingNumberError()

    return tracking_num

def validate_year(raw: str) -> int:
    """"
    Validates a given year and raises an exception if it is invalid.
    To be valid, a year must only contain digits and should be at least
    1900.

    :param raw: the year to validate.
    :return: the validated year, with all leading/trailing whitespace removed.
    """
    require_not_none(raw, "Year should not be None.")

    raw = raw.strip()

    try:
        year = int(raw)
    except ValueError:
        raise InvalidYearError()

    if year < MIN_BUS_YEAR:
        raise InvalidYearError()

    return year

def validate_model(raw: str) -> str:
    """"
    Validates a given model and raises an exception if it is invalid.
    To be valid, a model must not be empty or only whitespace.

    :param raw: the model to validate.
    :return: the validated model, with all leading/trailing whitespace removed.
    """
    require_not_none(raw, "Model should not be None.")

    raw = raw.strip()

    if not raw:
        raise EmptyModelError()

    return raw