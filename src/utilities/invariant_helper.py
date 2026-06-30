def require_not_none(obj, message: str) -> None:
    """
    Raises a ValueError with a given error message if `obj` is None.

    :param obj: the object to check for None.
    :param message: the error message to print if `obj` is None.
    """
    if obj is None:
        raise ValueError(message)

def require_state(condition: bool, message: str) -> None:
    """
    Raises a ValueError with a given error message if `condition` is False.

    :param condition: a boolean representing some condition.
    :param message: the error message to print if `condition` is False.
    """
    if not condition:
        raise ValueError(message)