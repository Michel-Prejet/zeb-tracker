from utilities.live_tracker_refactor.BlockIDFinder import BlockIDFinder
from utilities.live_tracker_refactor.StopScanner import StopScanner
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.GTFSReader import GTFSReader


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

    def scan_stops(self) -> None:
        self.stop_scanner.scan_all_stops_and_record_observations()

    def get_location_info_for_bus(self, bus_tracking_num: int) -> dict | None:
        """
        Uses the stop scan and the block ID finder to build a dictionary
        containing live location information for a given bus, including
        the stop ID, name, and coordinates; the route and destination; the
        block ID (possibly None); and the scheduled and estimated arrival times
        at the stop.
        Assumes that the stop scan has already been performed.

        :param bus_tracking_num: the tracking number of the bus for which to
        retrieve live location information.
        :return: a dictionary containing live location information for the
        given bus, or None if no location information was found.
        """
        observations = self.stop_scanner.observations.get_all_observations_for_bus(bus_tracking_num)
        latest_observation = self.stop_scanner.observations.get_latest_observation(bus_tracking_num)

        if latest_observation is None:
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
            "arrival": {
                "scheduled": latest_observation.scheduled_arrival,
                "estimated": latest_observation.estimated_arrival
            }
        }




