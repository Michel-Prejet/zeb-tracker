from domain.validation.exceptions.RunError import InvalidBlockIDError, InvalidRunDateError
from utilities.InvariantHelper import require_not_none
from datetime import date

MIN_BLOCK_ID_LENGTH = 3

def validate_block_id(raw: str) -> str:
    """
    Validates a given block ID and raises an exception if it is invalid.
    To be valid, a block ID must contain at least 3 non-blank characters that
    are only digits, except for exactly one dash not at the start or the end
    of the string. Removes all leading and trailing whitespace before
    validation.

    :param raw: the block number to validate.
    :return: the validated block ID, with all leading/trailing whitespace
    removed.
    """
    require_not_none(raw, "Block ID should not be None.")

    raw = raw.strip()

    if len(raw) < MIN_BLOCK_ID_LENGTH:
        raise InvalidBlockIDError()

    dash_index = raw.find('-')

    if dash_index in [-1, 0, len(raw) - 1] or dash_index != raw.rfind('-'):
        raise InvalidBlockIDError()

    for char in raw:
        if char != '-' and not char.isdigit():
            raise InvalidBlockIDError()

    return raw

def validate_date(raw: str) -> date:
    """
    Validates a given date string and raises an exception if it is
    not in the form YYYY-MM-DD. Removes all leading and trailing
    whitespace before validation.

    :param raw: the date string to validate.
    :return: the valid date object corresponding to `raw`.
    """
    require_not_none(raw, "Date should not be None.")

    raw = raw.strip()

    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise InvalidRunDateError()
