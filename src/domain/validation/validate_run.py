from constants.app_constants import NUM_BLOCK_ID_TOKENS
from domain.validation.exceptions.run_error import InvalidBlockIDError, InvalidRunDateError
from utilities.invariant_helper import require_not_none
from datetime import date


def validate_block_id(raw: str) -> str:
    """
    Validates a given block ID and raises an exception if it is invalid.
    To be valid, a block ID must contain exactly two numbers separated by a
    single dash.

    :param raw: the block number to validate.
    :return: the validated block ID, with all leading/trailing whitespace
    removed from each token.
    """
    require_not_none(raw, "Block ID should not be None.")

    raw = raw.strip()

    tokens = raw.split("-")
    if len(tokens) != NUM_BLOCK_ID_TOKENS:
        raise InvalidBlockIDError()

    tokens_numeric = []
    for token in tokens:
        token = token.strip()

        try:
            tokens_numeric.append(int(token))
        except ValueError:
            raise InvalidBlockIDError()

    return f"{tokens_numeric[0]}-{tokens_numeric[1]}"

def validate_date(raw: str) -> date:
    """
    Validates a given date string and raises an exception if it is
    not in the form YYYY-MM-DD. Removes all leading and trailing
    whitespace before validation.

    :param raw: the date string to validate.
    :return: the valid date object corresponding to the given string.
    """
    require_not_none(raw, "Date should not be None.")

    raw = raw.strip()

    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise InvalidRunDateError()
