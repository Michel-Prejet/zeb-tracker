from utilities.live_tracker.StopInfo import get_stop_info
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

STOP_LIST_FILE = "../gtfs/stops.txt"
MAX_WORKERS = 10

RED = "\033[31m"
COLOUR_RESET = "\033[0m"


def get_live_bus_locations() -> dict[int, dict]:
    """
    Scans all stops in the Winnipeg Transit API to determine the approximate
    location of each active bus.

    :return: a dictionary in which the keys are the bus tracking numbers and
    the values are dictionaries containing live information about that bus,
    including the current stop ID, name, and coordinates; the current route
    and destination; and the estimated arrival time of the bus at the stop.
    """
    locations: dict[int, dict] = dict()
    stops: list[int] = _get_all_stop_numbers()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_scan_stop, stop): stop
            for stop in stops
        }

        for future in as_completed(futures):
            stop_info = future.result()
            if stop_info is not None:
                _update_locations_from_stop_info(locations, stop_info)

    return locations

def _update_locations_from_stop_info(locations: dict[int, dict], stop_info: dict) -> None:
    """
    Uses the given API information for a stop to update the locations of buses
    in the given dictionary. If a bus is within 15 minutes of the stop and an
    earlier arrival hasn't been recorded for that bus in the dictionary, its
    live information in the dictionary is updated. Live information includes
    the current stop ID, coordinates, and name; the route and destination; and
    the estimated arrival time of the bus at the stop.

    :param locations: a dictionary in which the keys are bus tracking numbers
    and the values are dictionaries containing live information for that bus.
    :param stop_info: live information for a stop retrieved from the Winnipeg
    Transit API, which should include the stop ID, name, and coordinates, as
    well as a list of upcoming arrivals.
    """
    MAX_TIME_FROM_STOP = timedelta(minutes=15)
    curr_time = datetime.now()

    for bus in stop_info["buses"]:
        arrival_time = datetime.fromisoformat(bus["arrival_time_est"])
        time_until_arrival = arrival_time - curr_time

        if timedelta(seconds=0) <= time_until_arrival <= MAX_TIME_FROM_STOP:
            bus_tracking_num = int(bus["tracking_num"])

            live_info = {
                "stop_id": int(stop_info["id"]),
                "stop_name": stop_info["name"],
                "coordinates": stop_info["coordinates"],
                "route": bus["route"],
                "destination": bus["destination"],
                "arrival_time_est": bus["arrival_time_est"]
            }

            if bus_tracking_num not in locations:
                locations[bus_tracking_num] = live_info
            else:
                prev_arrival_time = datetime.fromisoformat(
                    locations[bus_tracking_num]["arrival_time_est"]
                )
                prev_time_until_arrival = prev_arrival_time - curr_time

                if time_until_arrival < prev_time_until_arrival:
                    locations[bus_tracking_num] = live_info

def _scan_stop(stop_number: int) -> dict | None:
    """
    Attempts to retrieve information from the Winnipeg Transit API for a stop
    with a given ID. If unsuccessful, the exception that occurred is printed.

    :param stop_number: the 5-digit number of the stop for which to retrieve
    information.
    :return: a dictionary containing information for the given stop (such as
    its ID, name, coordinates, and arrivals) or None if the information could
    not be retrieved.
    """
    try:
        return get_stop_info(stop_number)
    except Exception as e:
        print(f"{RED}Error scanning stop {stop_number}: {e}{COLOUR_RESET}")
        return None

def _get_all_stop_numbers() -> list[int]:
    """
    Reads all stops from the GTFS archive and creates a list containing each
    5-digit stop ID.
    :return: a list of integers containing every 5-digit stop ID in Winnipeg.
    """
    stops = []

    curr_line_num = 1
    with open(STOP_LIST_FILE, "r") as stops_input_file:
        stops_input_file.readline() # Skip header
        curr_line_num += 1

        for line in stops_input_file:
            next_stop_num_raw = line[:line.find(",")]

            try:
                stops.append(int(next_stop_num_raw))
            except ValueError:
                print(f"{RED}Could not convert {next_stop_num_raw} to int{COLOUR_RESET}")

        curr_line_num += 1

    return stops