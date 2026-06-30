from datetime import datetime, date
from utilities.live_tracker.winnipeg_transit_gtfs.gtfs_file_paths import GTFS_PATH, FEED_INFO_INPUT_FILE
from utilities.live_tracker.winnipeg_transit_gtfs.exceptions.transit_gtfs_error import MissingColumnError, \
    MissingTokenError, GTFSFileNotFoundError, GTFSOutdatedError, MalformedTokenError


START_DATE_COLUMN_HEADER = "feed_start_date"
END_DATE_COLUMN_HEADER = "feed_end_date"

class FeedInfoReader:
    """
    Parses the feed info file from Winnipeg Transit's GTFS archive to retrieve
    the start and end dates that define when the data is valid. Determines
    whether the GTFS data is out of date.
    """
    def __init__(self):
        try:
            with open(f"{GTFS_PATH}/{FEED_INFO_INPUT_FILE}", "r") as feed_info_file:
                self.input_file = feed_info_file

                # Find and validate the indices of each relevant column
                header = feed_info_file.readline()
                header_tokens = [t.strip() for t in header.split(",")]

                try:
                    self.start_date_col = header_tokens.index(START_DATE_COLUMN_HEADER)
                    self.end_date_col = header_tokens.index(END_DATE_COLUMN_HEADER)
                except ValueError:
                    raise MissingColumnError(FEED_INFO_INPUT_FILE)

                # Parse and validate the start/end dates
                self.curr_row = 2
                self.start_date, self.end_date = self._validate_and_parse_start_and_end_dates()
        except FileNotFoundError:
            raise GTFSFileNotFoundError(FEED_INFO_INPUT_FILE)

    def validate_feed_is_current(self) -> None:
        """
        Checks whether the GTFS data is out of date. Gets today's date and
        compares it to the start and end dates in the feed info file, and
        raises an exception if the current date is before the start date or
        after the end date.
        """
        curr_date = date.today()
        if curr_date < self.start_date or curr_date > self.end_date:
            raise GTFSOutdatedError()

    def _validate_and_parse_start_and_end_dates(self) -> tuple[date, date]:
        """
        Validates and parses the start and end dates read from the next row
        in the feed info GTFS file. If any tokens are missing or malformed,
        an exception will be raised. Expects dates in YYYYMMDD format.

        :return: a tuple of the form (START_DATE, END_DATE), where START_DATE
        and END_DATE are date objects.
        """
        NUM_DIGITS_IN_DATE = 8

        tokens = self.input_file.readline().split(",")

        num_tokens = len(tokens)
        if self.start_date_col >= num_tokens or self.end_date_col >= num_tokens:
            raise MissingTokenError(FEED_INFO_INPUT_FILE, self.curr_row)

        start_date_raw = tokens[self.start_date_col].strip()
        end_date_raw = tokens[self.end_date_col].strip()

        if not start_date_raw.isdigit() or len(start_date_raw) != NUM_DIGITS_IN_DATE:
            raise MalformedTokenError(FEED_INFO_INPUT_FILE, self.curr_row, START_DATE_COLUMN_HEADER)
        if not end_date_raw.isdigit() or len(end_date_raw) != NUM_DIGITS_IN_DATE:
            raise MalformedTokenError(FEED_INFO_INPUT_FILE, self.curr_row, END_DATE_COLUMN_HEADER)

        try:
            start_date = datetime.strptime(start_date_raw, "%Y%m%d").date()
        except ValueError:
            raise MalformedTokenError(FEED_INFO_INPUT_FILE, self.curr_row, START_DATE_COLUMN_HEADER)
        try:
            end_date = datetime.strptime(end_date_raw, "%Y%m%d").date()
        except ValueError:
            raise MalformedTokenError(FEED_INFO_INPUT_FILE, self.curr_row, END_DATE_COLUMN_HEADER)

        if start_date > end_date:
            raise MalformedTokenError(FEED_INFO_INPUT_FILE, self.curr_row, END_DATE_COLUMN_HEADER)

        return start_date, end_date