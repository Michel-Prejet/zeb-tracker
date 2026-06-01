from datetime import timedelta
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.exceptions.TransitGTFSError import MissingColumnError, \
    GTFSFileNotFoundError, MissingTokenError, InvalidStopIDError, InvalidTripIDError, InvalidArrivalTimeError
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.GTFSFilePaths import GTFS_PATH, STOP_TIMES_INPUT_FILE
from utilities.live_tracker_refactor.domain.Stop import STOP_NUMBER_LENGTH


STOP_ID_COLUMN_HEADER = "stop_id"
ARRIVAL_TIME_COLUMN_HEADER = "arrival_time"
TRIP_ID_COLUMN_HEADER = "trip_id"

class StopTimesReader:
    """
    Parses the stop times file from Winnipeg Transit's GTFS archive to create
    a dictionary that associates a stop ID and an arrival time with a list of
    corresponding trip IDs. Only accesses the stop ID, arrival time, and trip
    ID columns in the file.
    """

    def __init__(self):
        self.trip_id_finder: dict[int, dict[timedelta, list[int]]] = {}

        try:
            with open(f"{GTFS_PATH}/{STOP_TIMES_INPUT_FILE}", "r") as stop_times_file:
                self.input_file = stop_times_file

                # Find and validate the indices of each relevant column
                header = stop_times_file.readline()
                header_tokens = [t.strip() for t in header.split(",")]

                try:
                    self.stop_id_col = header_tokens.index(STOP_ID_COLUMN_HEADER)
                    self.arrival_time_col = header_tokens.index(ARRIVAL_TIME_COLUMN_HEADER)
                    self.trip_id_col = header_tokens.index(TRIP_ID_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(f"Missing column in {STOP_TIMES_INPUT_FILE}.")

                # Parse and validate each row/token to populate the trip ID finder
                self.curr_row = 2
                self._parse_gtfs_stop_times()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(f"{STOP_TIMES_INPUT_FILE} could not be opened.")

    def get(self) -> dict[int, dict[timedelta, list[int]]]:
        """
        Returns the trip ID finder dictionary created by this stop times reader.

        :return: a dictionary that maps stop IDs to another dictionary, which maps
        arrival times to a list of trip IDs (i.e. dict[STOP_ID][ARRIVAL_TIME]
        returns the list of trip IDs in which the bus arrives at the given stop at
        the given arrival time).
        """
        return self.trip_id_finder

    def _parse_gtfs_stop_times(self) -> None:
        """
        Parses the stop times GTFS file and populates the trip ID finder. The
        stop ID, arrival time, and trip ID are read from each row and added to
        the dictionary (i.e. the trip ID is added to the list found at
        trip_id_finder[stop_id][arrival_time]). An exception will be raised
        if any row or token is malformed.
        """
        for line in self.input_file:
            tokens = line.split(",")
            stop_id, arrival_time, trip_id = self._validate_and_parse_tokens(tokens)

            if stop_id not in self.trip_id_finder:
                self.trip_id_finder[stop_id] = {}
            if arrival_time not in self.trip_id_finder[stop_id]:
                self.trip_id_finder[stop_id][arrival_time] = []
            self.trip_id_finder[stop_id][arrival_time].append(trip_id)

            self.curr_row += 1

    def _validate_and_parse_tokens(self, tokens: list[str]) -> tuple[int, timedelta, int]:
        """
        Validates and parses the tokens read from a row in the stop times GTFS
        file. The given list should contain three tokens: the stop ID, the
        arrival time, and the trip ID. If any tokens are missing or malformed,
        an exception will be raised. Otherwise, the parsed tokens will be returned
        in a tuple.

        :param tokens: a list of raw strings read from a CSV line in the stop
        time GTFS file which should contain a stop ID, an arrival time, and a
        trip ID.
        :return: a tuple of the form (STOP_ID, ARRIVAL_TIME, TRIP_ID), where
        STOP_ID is 5-digit integer, ARRIVAL_TIME is a timedelta object, and
        TRIP_ID is an integer.
        """
        num_tokens = len(tokens)
        if (self.stop_id_col >= num_tokens or self.arrival_time_col >= num_tokens
                or self.trip_id_col >= num_tokens):
            raise MissingTokenError(f"Missing token in {STOP_TIMES_INPUT_FILE} on line {self.curr_row}.")

        stop_id_raw = tokens[self.stop_id_col].strip()
        arrival_time_raw = tokens[self.arrival_time_col].strip()
        trip_id_raw = tokens[self.trip_id_col].strip()

        if not stop_id_raw.isdigit() or len(stop_id_raw) != STOP_NUMBER_LENGTH:
            raise InvalidStopIDError(f"Invalid stop ID in {STOP_TIMES_INPUT_FILE} on line {self.curr_row}.")
        if not trip_id_raw.isdigit():
            raise InvalidTripIDError(f"Invalid trip ID in {STOP_TIMES_INPUT_FILE} on line {self.curr_row}.")

        arrival_time = parse_gtfs_time(arrival_time_raw,
                                        f"Invalid arrival time in {STOP_TIMES_INPUT_FILE} "
                                        f"on line {self.curr_row}.")
        return int(stop_id_raw), arrival_time, int(trip_id_raw)

def parse_gtfs_time(raw_time: str, err_msg="") -> timedelta:
    """
    Creates a timedelta object from a raw string. If the string is not
    of the form HH:MM:SS, an InvalidArrivalTimeError is raised.

    :param raw_time: the raw string to convert to a timedelta object.
    :param err_msg: the error message to pass to the exception if an error
    occurs.
    :return: a timedelta object created from the given string.
    """
    NUM_TOKENS = 3
    MAX_NUM_MINUTES = 60
    MAX_NUM_SECONDS = 60

    tokens = raw_time.split(":")
    if len(tokens) != NUM_TOKENS:
        raise InvalidArrivalTimeError(err_msg)
    for val in tokens:
        if not val.isdigit():
            raise InvalidArrivalTimeError(err_msg)

    hours, minutes, seconds = map(int, tokens)

    if minutes >= MAX_NUM_MINUTES or seconds >= MAX_NUM_SECONDS:
        raise InvalidArrivalTimeError(err_msg)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
