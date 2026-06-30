from utilities.live_tracker.winnipeg_transit_gtfs.file_readers.calendar_reader import CalendarReader
from utilities.live_tracker.winnipeg_transit_gtfs.gtfs_file_paths import GTFS_PATH, TRIPS_INPUT_FILE
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.transit_gtfs_error import GTFSFileNotFoundError, \
    MissingTokenError, MissingColumnError, MalformedTokenError


TRIP_ID_COLUMN_HEADER = "trip_id"
SERVICE_ID_COLUMN_HEADER = "service_id"
BLOCK_ID_COLUMN_HEADER = "block_id"

class TripsReader:
    """
    Parses the trips file from Winnipeg Transit's GTFS archive to create a
    dictionary that maps trip IDs to their respective block ID, ignoring any rows
    in which the service ID does not match today's service ID. Only accesses
    the trip ID, service ID, and block ID columns in the file.
    """

    def __init__(self):
        self.block_id_finder: dict[str, str] = {}

        try:
            with open(f"{GTFS_PATH}/{TRIPS_INPUT_FILE}", "r") as trips_file:
                self.input_file = trips_file

                # Find and validate the indices of each relevant column
                header = trips_file.readline()
                header_tokens = [t.strip() for t in header.split(",")]

                try:
                    self.trip_id_col = header_tokens.index(TRIP_ID_COLUMN_HEADER)
                    self.service_id_col = header_tokens.index(SERVICE_ID_COLUMN_HEADER)
                    self.block_id_col = header_tokens.index(BLOCK_ID_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(TRIPS_INPUT_FILE)

                # Get today's service ID
                calendar_reader = CalendarReader()
                self.curr_service_id = calendar_reader.get_current_service_id()

                # Parse and validate each row/token to populate the block ID finder
                self.curr_row = 2
                self._parse_gtfs_trips()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(TRIPS_INPUT_FILE)

    def get(self) -> dict[str, str]:
        """
        Returns the block ID finder dictionary created by this trips reader.

        :return: a dictionary that maps trip IDs to their corresponding block
        ID.
        """
        return self.block_id_finder

    def _parse_gtfs_trips(self) -> None:
        """
        Parses the trips GTFS file and populates the block ID finder. The trip
        ID and block ID are read from each row in which the service ID matches
        today's service ID, and they are added to the dictionary (i.e. the trip
        ID is mapped to the corresponding block ID). An exception will be raised
        if any row or token is malformed.
        """
        for line in self.input_file:
            tokens = line.split(",")
            validated_tokens = self._validate_and_parse_tokens(tokens)

            if validated_tokens is not None:
                trip_id, block_id = validated_tokens
                self.block_id_finder[trip_id] = block_id

            self.curr_row += 1

    def _validate_and_parse_tokens(self, tokens: list[str]) -> tuple[str, str] | None:
        """
        Validates and parses the tokens read from a row in the trips GTFS file.
        The given list should contain three tokens: the trip ID, service ID,
        and block ID. If any tokens are missing or malformed, an exception
        will be raised. If the service ID does not match the service ID
        associated with today's date, None is returned; otherwise the parsed
        tokens will be returned in a tuple.

        :param tokens: a list of raw strings read from a CSV line in the trips
        GTFS file which should contain a trip ID, service ID, and block ID.
        :return: a tuple of the form (TRIP_ID, BLOCK_ID), where TRIP_ID and
        BLOCK_ID are strings, if the service ID matches the service ID associated
        with today's date; or None if the service ID does not match the one
        associated with today's date.
        """
        num_tokens = len(tokens)
        if (self.trip_id_col >= num_tokens or self.service_id_col >= num_tokens
                or self.block_id_col >= num_tokens):
            raise MissingTokenError(TRIPS_INPUT_FILE, self.curr_row)

        trip_id = tokens[self.trip_id_col].strip()
        service_id = tokens[self.service_id_col].strip()
        block_id_raw = tokens[self.block_id_col].strip()

        if not _is_valid_block_id(block_id_raw):
            raise MalformedTokenError(TRIPS_INPUT_FILE, self.curr_row, BLOCK_ID_COLUMN_HEADER)

        if service_id != self.curr_service_id:
            return None

        block_id_parts = block_id_raw.split("-")
        block_id = f"{block_id_parts[1]}-{block_id_parts[2]}"

        return trip_id, block_id

def _is_valid_block_id(value: str) -> bool:
    """
    Determines whether a given string from the GTFS data is valid block ID. A
    valid block ID contains exactly two dashes.

    :param value: the string to validate.
    :return: True if the given string is a valid block ID, False otherwise.
    """
    NUM_DASHES_IN_BLOCK_ID = 2

    if value.count("-") != NUM_DASHES_IN_BLOCK_ID:
        return False

    return True
