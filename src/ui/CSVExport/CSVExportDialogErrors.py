class EmptyFileNameError(Exception):
    """
    Exception thrown when a file name is left empty or blank in an input field.
    """
    pass

class InvalidFolderPathError(Exception):
    """
    Exception thrown when a folder path is left empty or blank in an input field.
    """
    pass

class InvalidRunDataStartDateError(Exception):
    """
    Exception thrown when the start date provided for the run data is invalid.
    """
    pass