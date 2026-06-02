from datetime import timedelta, datetime
from utilities.live_tracker_refactor.BlockIDFinder import BlockIDFinder
from utilities.live_tracker_refactor.StopScanner import StopScanner
from utilities.live_tracker_refactor.TimeHelper import get_curr_time_as_timedelta
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.GTFSReader import GTFSReader


MAX_MINUTES_FROM_STOP = 15

class LiveBusTracker:
    """
    Retrieves live location information for buses using the Winnipeg Transit
    API and GTFS archive. Perform a scan on all stops (done on a separate thread),
    then ask for location information for a bus with a given tracking number.
    """

    def __init__(self):
        gtfs_reader = GTFSReader()
        self.stop_scanner = StopScanner(gtfs_reader)
        self.block_id_finder = BlockIDFinder(gtfs_reader)
        self.query_time: timedelta | None = None

    def scan_stops(self) -> None:
        self.query_time = get_curr_time_as_timedelta()
        self.stop_scanner.scan_all_stops_and_record_observations()

    def get_location_info_for_bus(self, bus_tracking_num: int) -> dict | None:
        """
        Uses the stop scan and the block ID finder to build a dictionary
        containing live location information for a given bus, including
        the stop ID, name, and coordinates; the route and destination; the
        block ID (possibly None); and the scheduled and estimated departure times
        at the stop. Only considers buses that are within 15 minutes of a stop.
        Assumes that the stop scan has already been performed.

        :param bus_tracking_num: the tracking number of the bus for which to
        retrieve live location information.
        :return: a dictionary containing live location information for the
        given bus, or None if no location information was found.
        """
        observations = self.stop_scanner.observations.get_all_observations_for_bus(bus_tracking_num)
        latest_observation = self.stop_scanner.observations.get_earliest_observation_for_bus(bus_tracking_num)

        if self.query_time is None or latest_observation is None:
            return None

        time_until_departure = latest_observation.estimated_departure - self.query_time
        if time_until_departure < timedelta(0) or time_until_departure > timedelta(minutes=MAX_MINUTES_FROM_STOP):
            return None

        block_id = self.block_id_finder.infer_block_id_from_gtfs(observations)

        return {
            "stop": {
                "id": latest_observation.stop.stop_id,
                "name": latest_observation.stop.name,
                "coordinates": {
                    "latitude": latest_observation.stop.coordinates.latitude,
                    "longitude": latest_observation.stop.coordinates.longitude
                }
            },
            "route": latest_observation.route,
            "destination": latest_observation.destination,
            "block_id": block_id,
            "departures": {
                "scheduled": latest_observation.scheduled_departure,
                "estimated": latest_observation.estimated_departure
            }
        }




