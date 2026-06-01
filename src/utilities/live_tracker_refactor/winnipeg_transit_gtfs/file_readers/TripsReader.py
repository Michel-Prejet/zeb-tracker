from utilities.live_tracker_refactor.winnipeg_transit_gtfs.file_readers.CalendarReader import CalendarReader
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.GTFSFilePaths import GTFS_PATH, TRIPS_INPUT_FILE
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.exceptions.TransitGTFSError import GTFSFileNotFoundError, \
    MissingTokenError, MissingColumnError, InvalidServiceIDError, InvalidTripIDError, InvalidBlockIDError


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
        self.block_id_finder: dict[int, str] = {}

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
                    raise MissingColumnError(f"Missing column in {TRIPS_INPUT_FILE}.")

                # Get today's service ID
                calendar_reader = CalendarReader()
                self.curr_service_id = calendar_reader.get_current_service_id()

                # Parse and validate each row/token to populate the block ID finder
                self.curr_row = 2
                self._parse_gtfs_trips()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(f"{TRIPS_INPUT_FILE} could not be opened.")

    def get(self) -> dict[int, str]:
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

    def _validate_and_parse_tokens(self, tokens: list[str]) -> tuple[int, str] | None:
        """
        Validates and parses the tokens read from a row in the trips GTFS file.
        The given list should contain three tokens: the trip ID, service ID,
        and block ID. If any tokens are missing or malformed, an exception
        will be raised. If the service ID does not match the service ID
        associated with today's date, None is returned; otherwise the parsed
        tokens will be returned in a tuple.

        :param tokens: a list of raw strings read from a CSV line in the trips
        GTFS file which should contain a trip ID, service ID, and block ID.
        :return: a tuple of the form (TRIP_ID, BLOCK_ID), where TRIP_ID is an
        integer and BLOCK_ID is a string, if the service ID matches the service
        ID associated with today's date; or None if the service ID does not match
        the one associated with today's date.
        """
        num_tokens = len(tokens)
        if (self.trip_id_col >= num_tokens or self.service_id_col >= num_tokens
                or self.block_id_col >= num_tokens):
            raise MissingTokenError(f"Missing token in {TRIPS_INPUT_FILE} on line {self.curr_row}.")

        trip_id_raw = tokens[self.trip_id_col].strip()
        service_id_raw = tokens[self.service_id_col].strip()
        block_id_raw = tokens[self.block_id_col].strip()

        if not trip_id_raw.isdigit():
            raise InvalidTripIDError(f"Invalid trip ID in {TRIPS_INPUT_FILE} on line {self.curr_row}.")
        if not service_id_raw.isdigit():
            raise InvalidServiceIDError(f"Invalid service ID in {TRIPS_INPUT_FILE} on line {self.curr_row}.")
        if not _is_valid_block_id(block_id_raw):
            raise InvalidBlockIDError(f"Invalid block ID in {TRIPS_INPUT_FILE} on line {self.curr_row}.")

        if int(service_id_raw) != self.curr_service_id:
            return None

        block_id_parts = block_id_raw.split("-")
        block_id = f"{block_id_parts[1]}-{block_id_parts[2]}"

        return int(trip_id_raw), block_id

def _is_valid_block_id(value: str) -> bool:
    """
    Determines whether a given string from the GTFS data is valid block ID. A
    valid block ID contains exactly two dashes (not at the first or last indices)
    and only digits (other than the dashes).

    :param value: the string to validate.
    :return: True if the given string is a valid block ID, False otherwise.
    """
    NUM_DASHES_IN_BLOCK_ID = 2

    if not value.replace("-", "").isdigit():
        return False
    if value.count("-") != NUM_DASHES_IN_BLOCK_ID:
        return False
    if not (value[0].isdigit() and value[len(value) - 1].isdigit()):
        return False

    return True
