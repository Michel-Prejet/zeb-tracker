class WtGTFSError(Exception):
    """
    Exception raised when there is a problem parsing data from
    the Winnipeg Transit GTFS archive.
    """


class GTFSOutdatedError(WtGTFSError):
    """
    Exception raised when the GTFS data is out of date.
    """
    pass

class StopNotFoundError(WtGTFSError):
    """
    Exception raised when a stop doesn't exist in the trip ID finder.
    """

class DepartureTimeNotFoundError(WtGTFSError):
    """
    Exception raised when an arrival time doesn't exist for a stop in the trip
    ID finder.
    """
    pass

class TripIDNotFoundError(WtGTFSError):
    """
    Exception raised when a trip ID doesn't exist in the block ID finder.
    """
    pass


class GTFSFileError(WtGTFSError):
    """
    Exception raised when an error occurs related to a specific GTFS file.
    """
    def __init__(self, filename: str):
        self.filename = filename

class GTFSFileNotFoundError(GTFSFileError):
    """
    Exception raised when a GTFS file could not be opened.
    """
    pass

class MissingColumnError(GTFSFileError):
    """
    Exception raised when a column could not be found in a GTFS
    CSV file.
    """


class GTFSRowError(GTFSFileError):
    """
    Exception raised when an error occurs related to a specific row in a
    GTFS file.
    """
    def __init__(self, filename: str, row: int, token_name: str | None = None):
        self.filename = filename
        self.row = row
        self.token_name = token_name

class MissingTokenError(GTFSRowError):
    """
    Exception raised when a token is missing from a row in a GTFS
    CSV file.
    """

class MalformedTokenError(GTFSRowError):
    """
    Exception raised when a token read from a GTFS CSV line is malformed.
    """
    pass

