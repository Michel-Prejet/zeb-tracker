from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable
from utilities.live_tracker.TimeHelper import parse_api_time
from utilities.live_tracker.TrackerErrorMessages import get_tracker_error_message
from utilities.live_tracker.domain.BusObservation import BusObservation
from utilities.live_tracker.domain.ObservationDict import ObservationDict
from utilities.live_tracker.winnipeg_transit_api.WTClient import get_stop_information_and_schedule
from utilities.live_tracker.winnipeg_transit_gtfs.GTFSReader import GTFSReader


MAX_WORKERS = 10

class StopScanner:
    """
    Scans stop information from the Winnipeg Transit API to populate an
    observation dictionary.
    """

    def __init__(self, gtfs_reader: GTFSReader):
        self.stops = gtfs_reader.get_all_stops()
        self.observations = ObservationDict()
        self.cancel_scan = False
        self.err_messages: list[str] = []

    def get_error_messages_and_clear_log(self) -> list[str]:
        err_messages = self.err_messages

        self.err_messages: list[str] = []

        return err_messages

    def scan_all_stops_and_record_observations(self,
        progress_callback: Callable[[int, int], None] | None = None) -> bool:
        """
        Scans all stops in the Winnipeg Transit API and records bus observations
        in this observation dictionary. The dictionary is cleared before the scan.
        The scan is done concurrently.

        :param progress_callback: optional callback accepting: completed_stops,
        total_stops.
        :return True if the scan was successful, False if the scan was cancelled.
        """
        self.observations = ObservationDict()

        total_stops = len(self.stops)
        completed_stops = 0
        if progress_callback is not None:
            progress_callback(completed_stops, total_stops)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(get_stop_information_and_schedule, stop): stop
                for stop in self.stops.keys()
            }

            for future in as_completed(futures):
                # Cancel the scan if the flag was set
                if self.cancel_scan:
                    for remaining_future in futures:
                        remaining_future.cancel()
                    self.cancel_scan = False
                    return False

                try:
                    stop_info = future.result()
                    self._add_observations_from_stop_api_data(stop_info)
                except Exception as e:
                    import traceback
                    traceback.print_exc()

                    err_msg = get_tracker_error_message(e)
                    self.err_messages.append(err_msg)
                    continue

                completed_stops += 1

                if progress_callback is not None:
                    progress_callback(completed_stops, total_stops)

        return True

    def cancel_stop_scan(self) -> None:
        """
        Requests that the current stop scan be cancelled.
        """
        self.cancel_scan = True

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

