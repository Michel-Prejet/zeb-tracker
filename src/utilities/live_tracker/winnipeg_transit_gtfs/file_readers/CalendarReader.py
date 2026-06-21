from datetime import datetime, date
from utilities.live_tracker.winnipeg_transit_gtfs.GTFSFilePaths import GTFS_PATH, CALENDAR_INPUT_FILE, \
    CALENDAR_EXCEPTIONS_INPUT_FILE
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.TransitGTFSError import GTFSFileNotFoundError, \
    MissingColumnError, MissingTokenError, MalformedTokenError, GTFSOutdatedError


# The column headers are also used as keys in the service ID finder.
# i.e. "saturday" maps to the service ID for saturdays.
SERVICE_ID_COLUMN_HEADER = "service_id"
START_DATE_COLUMN_HEADER = "start_date"
END_DATE_COLUMN_HEADER = "end_date"
MONDAY_COLUMN_HEADER = "monday"
TUESDAY_COLUMN_HEADER = "tuesday"
WEDNESDAY_COLUMN_HEADER = "wednesday"
THURSDAY_COLUMN_HEADER = "thursday"
FRIDAY_COLUMN_HEADER = "friday"
SATURDAY_COLUMN_HEADER = "saturday"
SUNDAY_COLUMN_HEADER = "sunday"

EXCEPTIONAL_DATE_COLUMN_HEADER = "date"
EXCEPTION_TYPE_COLUMN_HEADER = "exception_type"

ADD_SERVICE_EXCEPTION_TYPE = 1

class CalendarReader:
    """
    Parses the calendar and calendar dates files from Winnipeg Transit's GTFS
    archive to create two dictionaries: one that associates a date range to another
    dictionary, which associates each weekday with a list of service IDs; and another
    that associates any exceptional days (such as holidays) with alternate service
    IDs.
    """

    def __init__(self):
        self.service_id_finder: dict[tuple[date, date], dict[str, str]] = {}
        self.exceptional_days: dict[date, str] = {}

        # Populate the service ID finder
        try:
            with open(f"{GTFS_PATH}/{CALENDAR_INPUT_FILE}", "r") as calendar_file:
                self.input_file = calendar_file

                # Find and validate the indices of each relevant column
                header = calendar_file.readline()
                header_tokens = [t.strip() for t in header.split(",")]

                try:
                    self.service_id_col = header_tokens.index(SERVICE_ID_COLUMN_HEADER)
                    self.start_date_col = header_tokens.index(START_DATE_COLUMN_HEADER)
                    self.end_date_col = header_tokens.index(END_DATE_COLUMN_HEADER)
                    self.monday_col = header_tokens.index(MONDAY_COLUMN_HEADER)
                    self.tuesday_col = header_tokens.index(TUESDAY_COLUMN_HEADER)
                    self.wednesday_col = header_tokens.index(WEDNESDAY_COLUMN_HEADER)
                    self.thursday_col = header_tokens.index(THURSDAY_COLUMN_HEADER)
                    self.friday_col = header_tokens.index(FRIDAY_COLUMN_HEADER)
                    self.saturday_col = header_tokens.index(SATURDAY_COLUMN_HEADER)
                    self.sunday_col = header_tokens.index(SUNDAY_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(CALENDAR_INPUT_FILE)

                # Parse and validate each row/token to populate the service ID finder
                self.curr_row = 2
                self._parse_gtfs_calendar()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(CALENDAR_INPUT_FILE)

        # Find any exceptional days
        try:
            with open(f"{GTFS_PATH}/{CALENDAR_EXCEPTIONS_INPUT_FILE}", "r") as exceptional_dates_file:
                self.input_file = exceptional_dates_file

                # Find and validate the indices of each relevant column
                header = exceptional_dates_file.readline()
                header_tokens = [t.strip() for t in header.split(",")]

                try:
                    self.service_id_col_exceptional = header_tokens.index(SERVICE_ID_COLUMN_HEADER)
                    self.exceptional_date_col = header_tokens.index(EXCEPTIONAL_DATE_COLUMN_HEADER)
                    self.exception_type_col = header_tokens.index(EXCEPTION_TYPE_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(CALENDAR_EXCEPTIONS_INPUT_FILE)

                # Parse and validate each row/token to populate the exception days dictionary
                self.curr_row = 2
                self._parse_gtfs_exceptional_dates()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(CALENDAR_EXCEPTIONS_INPUT_FILE)
    
    def get_current_service_id(self) -> str:
        """
        Finds the service ID associated with today's date. If the current
        date is stored in the exceptional days dictionary, the associated service
        ID is returned. Otherwise, the service ID associated with the current day
        of the week for the current date range is returned. If the current date
        does not fit within any date range, a GTFSOutdatedError is raised.

        :return: the service ID associated with today's date.
        """
        curr_date = datetime.now().date()

        if curr_date in self.exceptional_days:
            return self.exceptional_days[curr_date]
        else:
            curr_day_of_week = curr_date.strftime("%A").lower()

            for start_date, end_date in self.service_id_finder:
                if start_date <= curr_date <= end_date:
                    return self.service_id_finder[start_date, end_date][curr_day_of_week]

        raise GTFSOutdatedError()

    def _parse_gtfs_calendar(self) -> None:
        """
        Parses the GTFS calendar file and populates the service ID finder.
        The service ID and the booleans corresponding to each weekday are
        read from each row. Any weekday marked as "1" is assigned the service
        ID for that row. An exception will be raised if any row or token is
        malformed, or if any weekday is assigned less than or more than one
        service ID.
        """
        for line in self.input_file:
            tokens = line.split(",")
            (service_id, start_date, end_date, monday, tuesday, wednesday,
             thursday, friday, saturday, sunday) = self._validate_and_parse_tokens_in_calendar(tokens)

            if (start_date, end_date) not in self.service_id_finder:
                self.service_id_finder[start_date, end_date] = {}

            days = [
                (monday, MONDAY_COLUMN_HEADER),
                (tuesday, TUESDAY_COLUMN_HEADER),
                (wednesday, WEDNESDAY_COLUMN_HEADER),
                (thursday, THURSDAY_COLUMN_HEADER),
                (friday, FRIDAY_COLUMN_HEADER),
                (saturday, SATURDAY_COLUMN_HEADER),
                (sunday, SUNDAY_COLUMN_HEADER)
            ]
            for has_service_id, key in days:
                if has_service_id:
                    if key in self.service_id_finder[start_date, end_date]:
                        raise MalformedTokenError(CALENDAR_INPUT_FILE, self.curr_row, "[flag]")
                    self.service_id_finder[start_date, end_date][key] = service_id

            self.curr_row += 1

        # Make sure that there is no day without a service ID.
        keys = [
            MONDAY_COLUMN_HEADER,
            TUESDAY_COLUMN_HEADER,
            WEDNESDAY_COLUMN_HEADER,
            THURSDAY_COLUMN_HEADER,
            FRIDAY_COLUMN_HEADER,
            SATURDAY_COLUMN_HEADER,
            SUNDAY_COLUMN_HEADER
        ]
        for date_range in self.service_id_finder:
            for key in keys:
                if key not in self.service_id_finder[date_range]:
                    raise MalformedTokenError(CALENDAR_INPUT_FILE, self.curr_row, SERVICE_ID_COLUMN_HEADER)

    def _parse_gtfs_exceptional_dates(self) -> None:
        """
        Parses the calendar dates GTFS file and populates exceptional days
        dictionary. The service ID, date, and exception type are read from each
        row. If an "Add service" exception type is found, the corresponding
        date is added to the dictionary and mapped to the service ID specified
        in that row. An exception will be raised if any row or token is
        malformed.
        """
        for line in self.input_file:
            tokens = line.split(",")
            service_id, exceptional_date, exception_type = (
                self._validate_and_parse_tokens_in_exceptional_dates(tokens))

            if exception_type == ADD_SERVICE_EXCEPTION_TYPE:
                self.exceptional_days[exceptional_date] = service_id

            self.curr_row += 1

    def _validate_and_parse_tokens_in_calendar(self, tokens: list[str]) -> tuple[str,
    date, date, bool, bool, bool, bool, bool, bool, bool]:
        """
        Validates and parses the tokens read from a row in the calendar GTFS
        file. The given list should contain 10 tokens: the service ID, the
        start/end dates, and booleans ("0" or "1") for each day of the week. If
        any tokens are missing or malformed, an exception will be raised. Otherwise,
        the parsed tokens will be returned in a tuple.

        :param tokens: a list of raw strings read from a CSV line in the
        calendar GTFS file which contain a service ID, start/end dates, and
        booleans ("0" or "1") for each day of the week.
        :return: a tuple of the form (SERVICE_ID, START_DATE, END_DATE, MONDAY,
        TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY), where SERVICE_ID
        is a string, START_DATE and END_DATE are date objects, and the remaining
        values are booleans.
        """
        VALID_SERVICE_FLAGS = ["0", "1"]

        num_tokens = len(tokens)
        if (self.service_id_col >= num_tokens or self.start_date_col >= num_tokens
            or self.end_date_col >= num_tokens or self.monday_col >= num_tokens
            or self.tuesday_col >= num_tokens or self.wednesday_col >= num_tokens
            or self.thursday_col >= num_tokens or self.friday_col >= num_tokens
            or self.saturday_col >= num_tokens or self.sunday_col >= num_tokens):
            raise MissingTokenError(CALENDAR_INPUT_FILE, self.curr_row)

        service_id = tokens[self.service_id_col].strip()
        start_date_raw = tokens[self.start_date_col].strip()
        end_date_raw = tokens[self.end_date_col].strip()
        monday_raw = tokens[self.monday_col].strip()
        tuesday_raw = tokens[self.tuesday_col].strip()
        wednesday_raw = tokens[self.wednesday_col].strip()
        thursday_raw = tokens[self.thursday_col].strip()
        friday_raw = tokens[self.friday_col].strip()
        saturday_raw = tokens[self.saturday_col].strip()
        sunday_raw = tokens[self.sunday_col].strip()

        if (monday_raw not in VALID_SERVICE_FLAGS or tuesday_raw not in VALID_SERVICE_FLAGS
                or wednesday_raw not in VALID_SERVICE_FLAGS or thursday_raw not in VALID_SERVICE_FLAGS
                or friday_raw not in VALID_SERVICE_FLAGS or saturday_raw not in VALID_SERVICE_FLAGS
                or sunday_raw not in VALID_SERVICE_FLAGS):
            raise MalformedTokenError(CALENDAR_INPUT_FILE, self.curr_row, "[flag]")

        try:
            start_date = datetime.strptime(start_date_raw, "%Y%m%d").date()
        except ValueError:
            raise MalformedTokenError(CALENDAR_INPUT_FILE, self.curr_row, START_DATE_COLUMN_HEADER)

        try:
            end_date = datetime.strptime(end_date_raw, "%Y%m%d").date()
        except ValueError:
            raise MalformedTokenError(CALENDAR_INPUT_FILE, self.curr_row, END_DATE_COLUMN_HEADER)

        return (service_id,
                start_date, end_date,
                _parse_gtfs_bool(monday_raw),
                _parse_gtfs_bool(tuesday_raw),
                _parse_gtfs_bool(wednesday_raw),
                _parse_gtfs_bool(thursday_raw),
                _parse_gtfs_bool(friday_raw),
                _parse_gtfs_bool(saturday_raw),
                _parse_gtfs_bool(sunday_raw))

    def _validate_and_parse_tokens_in_exceptional_dates(self, tokens: list[str]) -> tuple[str, date, int]:
        """
        Validates and parses the tokens read from a row in the calendar dates
        GTFS file. The given list should contain three tokens: the service ID
        to change, the exceptional date, and the exception type. If any tokens
        are missing or malformed, an exception will be raised. Otherwise, the
        parsed tokens will be returned in a tuple.

        :param tokens: a list of raw string read from a CSV line in the calendar
        dates GTFS file which should contain a service ID, a date in the form
        YYYYMMDD, and a number representing the exception type.
        :return: a tuple of the form (SERVICE_ID, DATE, EXCEPTION_TYPE), where
        SERVICE_ID is a string, EXCEPTION_TYPE is an integers, and DATE is a date
        object.
        """
        NUM_DIGITS_IN_DATE = 8

        num_tokens = len(tokens)
        if (self.service_id_col_exceptional >= num_tokens
                or self.exceptional_date_col >= num_tokens
                or self.exception_type_col >= num_tokens):
            raise MissingTokenError(CALENDAR_EXCEPTIONS_INPUT_FILE, self.curr_row)

        service_id = tokens[self.service_id_col_exceptional].strip()
        exceptional_date_raw = tokens[self.exceptional_date_col].strip()
        exception_type_raw = tokens[self.exception_type_col].strip()

        if not exceptional_date_raw.isdigit() or len(exceptional_date_raw) != NUM_DIGITS_IN_DATE:
            raise MalformedTokenError(CALENDAR_EXCEPTIONS_INPUT_FILE, self.curr_row, EXCEPTIONAL_DATE_COLUMN_HEADER)
        if not exception_type_raw.isdigit():
            raise MalformedTokenError(CALENDAR_EXCEPTIONS_INPUT_FILE, self.curr_row, EXCEPTION_TYPE_COLUMN_HEADER)

        return (service_id,
                datetime.strptime(exceptional_date_raw, "%Y%m%d").date(),
                int(exception_type_raw))

def _parse_gtfs_bool(value: str) -> bool:
    """
    Converts a string to a boolean. '0' is mapped to False and '1' is mapped
    to True. Assumes that the string is either '0' or '1'.

    :param value: the raw string to convert to a boolean.
    :return: True if the given string is '1'; False otherwise.
    """
    return value == "1"
