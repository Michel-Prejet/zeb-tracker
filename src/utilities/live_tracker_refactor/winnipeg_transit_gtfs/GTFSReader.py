from datetime import timedelta
from utilities.InvariantHelper import require_not_none, require_state
from utilities.live_tracker_refactor.domain.Stop import STOP_NUMBER_LENGTH, Stop
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.file_readers.FeedInfoReader import FeedInfoReader
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.file_readers.StopTimesReader import StopTimesReader
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.file_readers.StopsReader import StopsReader
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.file_readers.TripsReader import TripsReader
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.exceptions.TransitGTFSError import StopNotFoundError, \
    DepartureTimeNotFoundError, TripIDNotFoundError


class GTFSReader:
    """
    Uses the GTFS archive to map stop ID/scheduled departure time pairs
    to trip IDs, and trip IDs to block IDs. The constructor raises an
    exception if the GTFS archive is out-of-date.
    """

    def __init__(self):
        # Check if the GTFS archive is up-to-date
        feed_info_reader = FeedInfoReader()
        feed_info_reader.validate_feed_is_current()

        # Get the stop dictionary
        stops_reader = StopsReader()
        self.stop_dictionary = stops_reader.get()

        # Get trip ID finder
        stop_times_reader = StopTimesReader()
        self.trip_id_finder = stop_times_reader.get()

        # Get block ID finder
        trips_reader = TripsReader()
        self.block_id_finder = trips_reader.get()

    def get_all_stops(self) -> dict[int, Stop]:
        """
        :return: a dictionary that maps each 5-digit stop ID in Winnipeg
        Transit's GTFS archive to an associated stop object.
        """
        return self.stop_dictionary

    def get_trip_ids(self, stop_id: int, scheduled_departure_time: timedelta) -> list[int]:
        """
        Finds the list of trip IDs corresponding to a given departure time at
        a given stop. Raises an exception if the stop ID or the corresponding
        departure time weren't found in the GTFS archive.

        :param stop_id: the 5-digit ID of the stop.
        :param scheduled_departure_time: a timedelta object representing a
        departure time at the given stop.
        :return: a list of trip IDs for which there is a departure at the given
        stop at the given time.
        """
        require_not_none(stop_id, "Stop ID should not be None.")
        require_state(len(str(stop_id)) == STOP_NUMBER_LENGTH,
                      f"Stop ID should contain exactly {STOP_NUMBER_LENGTH} digits.")
        require_not_none(scheduled_departure_time,
                         "Scheduled departure time should not be None.")

        stop_departure_times_dict = self.trip_id_finder.get(stop_id)
        if stop_departure_times_dict is None:
            raise StopNotFoundError(f"Stop {stop_id} doesn't exist in the trip ID finder.")

        trip_ids = stop_departure_times_dict.get(scheduled_departure_time)
        if trip_ids is None:
            raise DepartureTimeNotFoundError(f"Departure time {scheduled_departure_time} doesn't "
                                           f"exist in the trip ID finder for stop {stop_id}.")

        require_state(len(trip_ids) >= 1,
                      "Trip ID list should not be empty.")
        return trip_ids

    def get_block_id(self, trip_id: int) -> str:
        """
        Finds the block ID associated with the given trip ID. Raises an
        exception if the trip ID wasn't found in the GTFS archive.

        :param trip_id: the trip ID to map to a block ID.
        :return: the block ID associated with the given trip ID.
        """
        require_not_none(trip_id, "Trip ID should not be None.")

        block_id = self.block_id_finder.get(trip_id)
        if block_id is None:
            raise TripIDNotFoundError(f"Trip ID {trip_id} doesn't exist in the block ID finder.")

        return block_id



