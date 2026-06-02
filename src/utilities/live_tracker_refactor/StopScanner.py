from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from utilities.live_tracker_refactor.TimeHelper import parse_api_time
from utilities.live_tracker_refactor.domain.BusObservation import BusObservation
from utilities.live_tracker_refactor.domain.ObservationDict import ObservationDict
from utilities.live_tracker_refactor.winnipeg_transit_api.WTClient import get_stop_information_and_schedule
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.GTFSReader import GTFSReader


MAX_WORKERS = 15

class StopScanner:
    """
    Scans stop information from the Winnipeg Transit API to populate an
    observation dictionary.
    """

    def __init__(self, gtfs_reader: GTFSReader):
        self.stops = gtfs_reader.get_all_stops()
        self.observations = ObservationDict()

    def scan_all_stops_and_record_observations(self) -> None:
        """
        Scans all stops in the Winnipeg Transit API and records bus observations
        in this observation dictionary. The dictionary is cleared before the scan.
        The scan is done concurrently.
        """
        self.observations = ObservationDict()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(get_stop_information_and_schedule, stop): stop
                for stop in self.stops.keys()
            }

            for future in as_completed(futures):
                stop_id = futures[future]

                try:
                    stop_info = future.result()
                    self._add_observations_from_stop_api_data(stop_info)
                except Exception as e:
                    print(f"Error scanning stop {stop_id}: {e}")
                    continue

    def _add_observations_from_stop_api_data(self, stop_info: dict) -> None:
        """
        Creates a bus observation for each arrival in the given data and adds
        it to the observation dictionary. Assumes that all data is properly
        formatted.

        :param stop_info: a dictionary containing relevant stop info, including
        the stop ID and a list of arrivals, each of which should contain the
        bus tracking number, route, destination, and scheduled/estimated departure
        times.
        """
        stop_id = stop_info["id"]
        stop = self.stops[stop_id]

        for bus_obs in stop_info["buses"]:
            tracking_num = bus_obs["tracking_num"]
            route = str(bus_obs["route"])
            destination = bus_obs["destination"]
            scheduled_departure_time = parse_api_time(bus_obs["departures"]["scheduled"])
            estimated_departure_time = parse_api_time(bus_obs["departures"]["estimated"])

            observation = BusObservation(stop, route, destination, tracking_num,
                                         scheduled_departure_time, estimated_departure_time)
            self.observations.add_observation(observation)


