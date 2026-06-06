from utilities.live_tracker.domain.Coordinates import MIN_LATITUDE, MAX_LATITUDE, MAX_LONGITUDE, MIN_LONGITUDE, \
    Coordinates
from utilities.live_tracker.domain.Stop import Stop, STOP_NUMBER_LENGTH
from utilities.live_tracker.winnipeg_transit_gtfs.GTFSFilePaths import GTFS_PATH, STOPS_INPUT_FILE
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.TransitGTFSError import GTFSFileNotFoundError, \
    MissingColumnError, MissingTokenError, InvalidStopIDError, EmptyStopNameError, InvalidStopLongitudeError, \
    InvalidStopLatitudeError
import csv


STOP_ID_COLUMN_HEADER = "stop_id"
STOP_NAME_COLUMN_HEADER = "stop_name"
STOP_LATITUDE_COLUMN_HEADER = "stop_lat"
STOP_LONGITUDE_COLUMN_HEADER = "stop_lon"

class StopsReader:
    """
    Parses the stops file from Winnipeg Transit's GTFS archive to create a
    dictionary that maps each stop ID to an associated stop object. Only
    accesses the stop ID, name, latitude, and longitude columns in the file.
    """
    def __init__(self):
        self.all_stops: dict[int, Stop] = {}

        try:
            with open(f"{GTFS_PATH}/{STOPS_INPUT_FILE}", "r") as stops_file:
                self.reader = csv.reader(stops_file)

                # Find and validate the indices of each relevant column
                header_tokens = [t.strip() for t in next(self.reader)]

                try:
                    self.stop_id_col = header_tokens.index(STOP_ID_COLUMN_HEADER)
                    self.stop_name_col = header_tokens.index(STOP_NAME_COLUMN_HEADER)
                    self.stop_latitude_col = header_tokens.index(STOP_LATITUDE_COLUMN_HEADER)
                    self.stop_longitude_col = header_tokens.index(STOP_LONGITUDE_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(f"Missing column in {STOPS_INPUT_FILE}.",
                                             STOPS_INPUT_FILE)

                # Parse and validate each row/token to populate the stop dictionary
                self.curr_row = 2
                self._parse_stops()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(f"{STOPS_INPUT_FILE} could not be opened.",
                                        STOPS_INPUT_FILE)

    def get(self) -> dict[int, Stop]:
        """
        Returns the stop dictionary created by this stops reader.

        :return: a dictionary that maps 5-digit stop IDs to the corresponding
        stop object created from GTFS data.
        """
        return self.all_stops

    def _parse_stops(self) -> None:
        """
        Parses the stops GTFS file and populates the stops dictionary. The stop
        ID, name, and coordinates are read from each row and a Stop object is
        created, then added to the dictionary with its ID as the key.
        """
        for tokens in self.reader:
            stop_id, stop_name, latitude, longitude = self._validate_and_parse_tokens(tokens)

            self.all_stops[stop_id] = Stop(stop_name, stop_id, Coordinates(latitude, longitude))

            self.curr_row += 1

    def _validate_and_parse_tokens(self, tokens: list[str]) -> tuple[int, str, float, float]:
        """
        Validates and parses the tokens read from a row in the stops GTFS file.
        The given list should contain four tokens: the stop's ID, name, latitude,
        and longitude. If any tokens are missing or malformed, an exception will
        be raised. Otherwise, the parsed tokens will be returned in a tuple.

        :param tokens: a list of raw strings read from a CSV line in the stops
        GTFS file which should contain a stop ID, name, latitude, and longitude.
        :return: a tuple of the form (STOP_ID, STOP_NAME, LATITUDE, LONGITUDE),
        where STOP_ID is a 5-digit integer, STOP_NAME is a non-empty string,
        and LATITUDE and LONGITUDE are floats.
        """
        num_tokens = len(tokens)
        if (self.stop_id_col >= num_tokens or self.stop_name_col >= num_tokens
            or self.stop_latitude_col >= num_tokens or self.stop_longitude_col >= num_tokens):
            raise MissingTokenError(f"Missing token in {STOPS_INPUT_FILE} on line {self.curr_row}.",
                                    STOPS_INPUT_FILE, self.curr_row)

        stop_id_raw = tokens[self.stop_id_col].strip()
        stop_name = tokens[self.stop_name_col].strip()
        stop_latitude_raw = tokens[self.stop_latitude_col].strip()
        stop_longitude_raw = tokens[self.stop_longitude_col].strip()

        if not stop_id_raw.isdigit() or len(stop_id_raw) != STOP_NUMBER_LENGTH:
            raise InvalidStopIDError(f"Invalid stop ID in {STOPS_INPUT_FILE} on line {self.curr_row}.",
                                     STOPS_INPUT_FILE, self.curr_row)
        if len(stop_name) == 0:
            raise EmptyStopNameError(f"Empty stop name in {STOPS_INPUT_FILE} on line {self.curr_row}.",
                                     STOPS_INPUT_FILE, self.curr_row)

        try:
            stop_latitude = float(stop_latitude_raw)
        except ValueError:
            raise InvalidStopLatitudeError(f"Invalid stop latitude in {STOPS_INPUT_FILE} on line {self.curr_row}.",
                                           STOPS_INPUT_FILE, self.curr_row)
        if stop_latitude < MIN_LATITUDE or stop_latitude > MAX_LATITUDE:
            raise InvalidStopLatitudeError(f"Stop latitude in {STOPS_INPUT_FILE} is not "
                                           f"in the interval [{MIN_LATITUDE}, {MAX_LATITUDE}].",
                                           STOPS_INPUT_FILE, self.curr_row)

        try:
            stop_longitude = float(stop_longitude_raw)
        except ValueError:
            raise InvalidStopLongitudeError(f"Invalid stop longitude in {STOPS_INPUT_FILE} on line {self.curr_row}.",
                                            STOPS_INPUT_FILE, self.curr_row)
        if stop_longitude < MIN_LONGITUDE  or stop_longitude > MAX_LONGITUDE:
            raise InvalidStopLongitudeError(f"Stop longitude in {STOPS_INPUT_FILE} is not "
                                           f"in the interval [{MIN_LONGITUDE}, {MAX_LONGITUDE}].",
                                            STOPS_INPUT_FILE, self.curr_row)

        return int(stop_id_raw), stop_name, stop_latitude, stop_longitude
