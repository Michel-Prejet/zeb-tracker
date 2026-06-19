from utilities.live_tracker.winnipeg_transit_api.exceptions.TransitAPIError import MissingAPIKeyError, WtTimeoutError, \
    WtConnectionError, WtAuthError, WtHTTPError, WtResponseError, WtClientError, WtAPIError, WtParsingError
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.TransitGTFSError import WtGTFSError, GTFSOutdatedError, \
    StopNotFoundError, DepartureTimeNotFoundError, TripIDNotFoundError, GTFSFileError, GTFSFileNotFoundError, \
    MissingColumnError, GTFSRowError, MissingTokenError, MalformedTokenError


def get_tracker_error_message(e: Exception):
    """
    :return: the error message corresponding to the given exception caught
    from the live tracker utility.
    """
    match e:
        case MissingAPIKeyError():
            return "The API key could not be located."
        case WtTimeoutError():
            return "The API request timed out."
        case WtConnectionError():
            return "Could not connect to the API."
        case WtAuthError():
            return "The API key was rejected."
        case WtHTTPError():
            return f"HTTP error {e.error_code}"
        case WtResponseError():
            return "The API returned malformed or unexpected data."
        case WtClientError():
            return "An unspecified API communication error occurred."
        case WtParsingError():
            return f"Error parsing API data: {e.attribute_name}.\n{e.malformed_data}"
        case WtAPIError():
            return "An unspecified API error occurred."
        case GTFSOutdatedError():
            return "The GTFS archive is outdated."
        case StopNotFoundError():
            return "The GTFS archive was asked for a stop ID that doesn't exist."
        case DepartureTimeNotFoundError():
            return "The GTFS archive was asked for a departure time that doesn't exist."
        case TripIDNotFoundError():
            return "The GTFS archive was asked for a trip ID that doesn't exist."
        case GTFSFileNotFoundError():
            return f"{e.filename} could not be found in the GTFS archive."
        case MissingColumnError():
            return f"{e.filename} has missing column(s) in the GTFS archive."
        case MissingTokenError():
            return f"Missing token in {e.filename} on row {e.row}."
        case MalformedTokenError():
            return f"Malformed token in {e.filename} on row {e.row}."
        case GTFSRowError():
            return f"Unspecified GTFS error in {e.filename} on row {e.row}."
        case GTFSFileError():
            return f"Unspecified error with {e.filename} in the GTFS archive."
        case WtGTFSError():
            return "An unspecified GTFS error occurred."
        case _:
            return "An unspecified error occurred."