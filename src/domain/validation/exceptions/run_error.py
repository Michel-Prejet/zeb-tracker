class RunError(Exception):
    """
    Exception thrown when any given run attributes are invalid.
    """
    pass

class InvalidBlockIDError(RunError):
    pass

class InvalidRunDateError(RunError):
    pass