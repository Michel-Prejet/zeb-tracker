from datetime import timedelta
from utilities.live_tracker.TimeHelper import parse_gtfs_time
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.TransitGTFSError import MissingColumnError, \
    GTFSFileNotFoundError, MissingTokenError, MalformedTokenError
from utilities.live_tracker.winnipeg_transit_gtfs.GTFSFilePaths import GTFS_PATH, STOP_TIMES_INPUT_FILE
from utilities.live_tracker.domain.Stop import STOP_NUMBER_LENGTH


STOP_ID_COLUMN_HEADER = "stop_id"
DEPARTURE_TIME_COLUMN_HEADER = "departure_time"
TRIP_ID_COLUMN_HEADER = "trip_id"

class StopTimesReader:
    """
    Parses the stop times file from Winnipeg Transit's GTFS archive to create
    a dictionary that associates a stop ID and a departure time with a list of
    corresponding trip IDs. Only accesses the stop ID, departure time, and trip
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
                    self.departure_time_col = header_tokens.index(DEPARTURE_TIME_COLUMN_HEADER)
                    self.trip_id_col = header_tokens.index(TRIP_ID_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(STOP_TIMES_INPUT_FILE)

                # Parse and validate each row/token to populate the trip ID finder
                self.curr_row = 2
                self._parse_gtfs_stop_times()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(STOP_TIMES_INPUT_FILE)

    def get(self) -> dict[int, dict[timedelta, list[int]]]:
        """
        Returns the trip ID finder dictionary created by this stop times reader.

        :return: a dictionary that maps stop IDs to another dictionary, which maps
        departure times to a list of trip IDs (i.e. dict[STOP_ID][DEPARTURE_TIME]
        returns the list of trip IDs in which the bus arrives at the given stop at
        the given departure time).
        """
        return self.trip_id_finder

    def _parse_gtfs_stop_times(self) -> None:
        """
        Parses the stop times GTFS file and populates the trip ID finder. The
        stop ID, departure time, and trip ID are read from each row and added to
        the dictionary (i.e. the trip ID is added to the list found at
        trip_id_finder[stop_id][departure_time]). An exception will be raised
        if any row or token is malformed.
        """
        for line in self.input_file:
            tokens = line.split(",")
            stop_id, departure_time, trip_id = self._validate_and_parse_tokens(tokens)

            if stop_id not in self.trip_id_finder:
                self.trip_id_finder[stop_id] = {}
            if departure_time not in self.trip_id_finder[stop_id]:
                self.trip_id_finder[stop_id][departure_time] = []
            self.trip_id_finder[stop_id][departure_time].append(trip_id)

            self.curr_row += 1

    def _validate_and_parse_tokens(self, tokens: list[str]) -> tuple[int, timedelta, int]:
        """
        Validates and parses the tokens read from a row in the stop times GTFS
        file. The given list should contain three tokens: the stop ID, the
        departure time, and the trip ID. If any tokens are missing or malformed,
        an exception will be raised. Otherwise, the parsed tokens will be returned
        in a tuple.

        :param tokens: a list of raw strings read from a CSV line in the stop
        time GTFS file which should contain a stop ID, a departure time, and a
        trip ID.
        :return: a tuple of the form (STOP_ID, DEPARTURE_TIME, TRIP_ID), where
        STOP_ID is 5-digit integer, DEPARTURE_TIME is a timedelta object, and
        TRIP_ID is an integer.
        """
        num_tokens = len(tokens)
        if (self.stop_id_col >= num_tokens or self.departure_time_col >= num_tokens
                or self.trip_id_col >= num_tokens):
            raise MissingTokenError(STOP_TIMES_INPUT_FILE, self.curr_row)

        stop_id_raw = tokens[self.stop_id_col].strip()
        departure_time_raw = tokens[self.departure_time_col].strip()
        trip_id_raw = tokens[self.trip_id_col].strip()

        if not stop_id_raw.isdigit() or len(stop_id_raw) != STOP_NUMBER_LENGTH:
            raise MalformedTokenError(STOP_TIMES_INPUT_FILE, self.curr_row, STOP_ID_COLUMN_HEADER)
        if not trip_id_raw.isdigit():
            raise MalformedTokenError(STOP_TIMES_INPUT_FILE, self.curr_row, TRIP_ID_COLUMN_HEADER)

        departure_time = parse_gtfs_time(departure_time_raw,
                                        STOP_TIMES_INPUT_FILE, self.curr_row)
        return int(stop_id_raw), departure_time, int(trip_id_raw)
