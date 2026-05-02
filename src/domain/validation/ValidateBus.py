from domain.Bus import Bus
from domain.validation.exceptions.BusError import InvalidTrackingNumberError, InvalidYearError, EmptyModelError
from utilities.InvariantHelper import require_not_none


TRACKING_NUMBER_LENGTH = 3

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

    if len(raw) != TRACKING_NUMBER_LENGTH:
        raise InvalidTrackingNumberError()

    try:
        return int(raw)
    except ValueError:
        raise InvalidTrackingNumberError()

def validate_year(raw: str) -> int:
    """"
    Validates a given year and raises an exception if it is invalid.
    To be valid, a year must only contain digits and should be at least
    2000.

    :param raw: the year to validate.
    :return: the validated year, with all leading/trailing whitespace removed.
    """
    require_not_none(raw, "Year should not be None.")

    raw = raw.strip()

    try:
        result = int(raw)
        if result < Bus.MIN_YEAR:
            raise InvalidYearError()
        else:
            return result
    except ValueError:
        raise InvalidYearError()

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