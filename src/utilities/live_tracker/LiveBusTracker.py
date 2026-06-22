from datetime import timedelta, datetime
from typing import Callable
from utilities.InvariantHelper import require_state
from utilities.live_tracker.BlockIDFinder import BlockIDFinder
from utilities.live_tracker.StopScanner import StopScanner
from utilities.live_tracker.TimeHelper import get_curr_time_as_timedelta
from utilities.live_tracker.TrackerErrorMessages import get_tracker_error_message
from utilities.live_tracker.winnipeg_transit_gtfs.GTFSReader import GTFSReader


MAX_MINUTES_FROM_STOP = 15

class LiveBusTracker:
    """
    Retrieves live location information for buses using the Winnipeg Transit
    API and GTFS archive. Perform a scan on all stops (done on a separate thread),
    then ask for location information for a bus with a given tracking number.
    """

    def __init__(self, progress_callback: Callable[[int, int], None] | None = None):
        self.query_time: datetime | None = None
        self.query_time_delta: timedelta | None = None
        self.progress_callback = progress_callback
        self.err_messages: list[str] = []

        self.gtfs_read = False

    def read_gtfs(self) -> None:
        gtfs_reader = GTFSReader()
        self.stop_scanner = StopScanner(gtfs_reader)
        self.block_id_finder = BlockIDFinder(gtfs_reader)

        self.gtfs_read = True

    def scan_stops(self) -> bool:
        """
        Gathers location information for arrivals at all stops in the Winnipeg
        Transit API.

        :return: True if the scan was successful, False if the scan was cancelled
        or unsuccessful.
        """
        require_state(self.gtfs_read, "GTFS should have been read before scanning stops.")

        self.query_time = datetime.now()
        self.query_time_delta = get_curr_time_as_timedelta()

        return self.stop_scanner.scan_all_stops_and_record_observations(self.progress_callback)

    def cancel_stop_scan(self) -> None:
        if self.gtfs_read:
            self.stop_scanner.cancel_stop_scan()

    def get_location_info_for_bus(self, bus_tracking_num: int) -> dict | None:
        """
        Uses the stop scan and the block ID finder to build a dictionary
        containing live location information for a given bus, including
        the stop ID, name, and coordinates; the route and destination; the
        block ID (possibly missing); and the scheduled and estimated departure times
        at the stop. Only considers buses that are within 15 minutes of a stop.
        Assumes that the gtfs read and the stop scan have already been performed.

        :param bus_tracking_num: the tracking number of the bus for which to
        retrieve live location information.
        :return: a dictionary containing live location information for the
        given bus, or None if no location information was found.
        """
        require_state(self.gtfs_read, "GTFS should have been read before retrieving location info.")

        observations = self.stop_scanner.observations.get_all_observations_for_bus(bus_tracking_num)
        current_observation = self.stop_scanner.observations.get_most_current_observation_for_bus(bus_tracking_num)

        if self.query_time_delta is None or current_observation is None:
            return None

        time_until_departure = current_observation.estimated_departure - self.query_time_delta
        if time_until_departure < timedelta(0) or time_until_departure > timedelta(minutes=MAX_MINUTES_FROM_STOP):
            return None

        block_id = self.block_id_finder.infer_block_id_from_gtfs(observations)

        result = {
            "stop": {
                "id": current_observation.stop.stop_id,
                "name": current_observation.stop.name,
                "coordinates": {
                    "latitude": current_observation.stop.coordinates.latitude,
                    "longitude": current_observation.stop.coordinates.longitude
                }
            },
            "route": current_observation.route,
            "destination": current_observation.destination,
            "departures": {
                "scheduled": current_observation.scheduled_departure,
                "estimated": current_observation.estimated_departure
            },
            "query_time": self.query_time.isoformat()
        }

        if block_id is not None:
            result["block_id"] = block_id

        return result

    def get_error_messages(self) -> list[str]:
        """
        Returns a list of error messages logged since the last time they
        were retrieved, then resets the list.

        :return: a list of strings containing all error messages reported
        since the last time they were retrieved.
        """
        if self.gtfs_read:
            stop_scan_errors = self.stop_scanner.get_error_messages_and_clear_log()
            result = self.err_messages + stop_scan_errors
        else:
            result = self.err_messages

        self.err_messages: list[str] = []

        return result

    def log_error(self, e: Exception) -> None:
        message = get_tracker_error_message(e)
        self.err_messages.append(message)




