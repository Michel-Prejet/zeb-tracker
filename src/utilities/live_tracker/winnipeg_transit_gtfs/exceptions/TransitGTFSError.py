class TransitGTFSError(Exception):
    """
    Exception raised when there is a problem parsing data from
    the Winnipeg Transit GTFS archive.
    """
    pass

class GTFSOutdatedError(TransitGTFSError):
    """
    Exception raised when the GTFS data is out of date.
    """
    pass

class StopNotFoundError(TransitGTFSError):
    """
    Exception raised when a stop doesn't exist in the trip ID finder.
    """
    pass

class DepartureTimeNotFoundError(TransitGTFSError):
    """
    Exception raised when an arrival time doesn't exist for a stop in the trip
    ID finder.
    """
    pass

class TripIDNotFoundError(TransitGTFSError):
    """
    Exception raised when a trip ID doesn't exist in the block ID finder.
    """
    pass

class GTFSFileNotFoundError(TransitGTFSError):
    """
    Exception raised when a GTFS file could not be opened.
    """
    pass

class MissingColumnError(TransitGTFSError):
    """
    Exception raised when a column could not be found in a GTFS
    CSV file.
    """
    pass

class MissingTokenError(TransitGTFSError):
    """
    Exception raised when a token is missing from a row in a GTFS
    CSV file.
    """
    pass

class MalformedTokenError(TransitGTFSError):
    """
    Exception raised when a token read from a GTFS CSV line is malformed.
    """
    pass
class InvalidStopIDError(MalformedTokenError): pass
class InvalidDepartureTimeError(MalformedTokenError): pass
class InvalidTripIDError(MalformedTokenError): pass
class InvalidStartDateError(MalformedTokenError): pass
class InvalidEndDateError(MalformedTokenError): pass
class InvalidServiceIDError(MalformedTokenError): pass
class InvalidServiceFlagError(MalformedTokenError): pass
class DuplicateServiceIDError(MalformedTokenError): pass
class MissingServiceIDError(MalformedTokenError): pass
class InvalidExceptionalDateError(MalformedTokenError): pass
class InvalidExceptionTypeError(MalformedTokenError): pass
class InvalidBlockIDError(MalformedTokenError): pass
class EmptyStopNameError(MalformedTokenError): pass
class InvalidStopLatitudeError(MalformedTokenError): pass
class InvalidStopLongitudeError(MalformedTokenError): pass

