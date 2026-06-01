from datetime import timedelta
from utilities.InvariantHelper import require_state


STOP_TIMES_INPUT_FILE = "../gtfs/stop_times.txt"
TRIPS_INPUT_FILE = "../gtfs/trips.txt"

RED = "\033[31m"
COLOUR_RESET = "\033[0m"

def add_block_ids_to_bus_location_info(location_info: dict[int, dict],
                                       location_observations: dict[int, list[tuple[timedelta, int]]]) -> None:
    arrival_times_to_stops_to_trips = get_all_arrival_times_for_all_stops()
    trips_to_blocks = get_all_block_ids_for_all_trip_ids()

    for bus in location_observations:
        inferred_block_id = get_block_id(location_observations[bus],
                                         arrival_times_to_stops_to_trips,
                                         trips_to_blocks)
        if bus in location_info and inferred_block_id is not None:
            location_info[bus]["block_id"] = inferred_block_id

def get_block_id(stop_ids_and_arrival_times: list[tuple[timedelta, int]],
                 arrival_times_to_stops_to_trips,
                 trips_to_blocks) -> str | None:
    """
    Attempts to infer the block ID from a list of (ARRIVAL_TIME, STOP_ID) pairs.
    Gets the list of trip IDs corresponding to each pair, maps them to their
    corresponding block IDs, and returns the most commonly occurring block ID.

    :param stop_ids_and_arrival_times: a list of (ARRIVAL_TIME, STOP_ID) tuples
    recorded for a specific bus from the Winnipeg Transit API.
    :param arrival_times_to_stops_to_trips:
    :param trips_to_blocks:
    :return: the block ID inferred from the given list of tuples, or None if
    no block ID could be found based on the tuple list.
    """
    MIN_NUM_BLOCK_ID_OCCURRENCES_FOR_INFERENCE = 3

    require_state(len(stop_ids_and_arrival_times) >= 1,
                  "STOP_ID, ARRIVAL_TIME tuple list should not be empty.")

    block_id_counts: dict[str, int] = {}
    for i in range(len(stop_ids_and_arrival_times)):
        trip_ids = arrival_times_to_stops_to_trips[stop_ids_and_arrival_times[i][0]][stop_ids_and_arrival_times[i][1]]

        for trip_id in trip_ids:
            block_id = trips_to_blocks[trip_id]
            if block_id not in block_id_counts:
                block_id_counts[block_id] = 1
            else:
                block_id_counts[block_id] += 1

    most_common_block_id = max(block_id_counts, key=block_id_counts.get)
    max_number_occurrences = block_id_counts[most_common_block_id]

    if max_number_occurrences <= MIN_NUM_BLOCK_ID_OCCURRENCES_FOR_INFERENCE:
        return None

    return max(block_id_counts, key=block_id_counts.get)

def get_all_block_ids_for_all_trip_ids() -> dict:
    """
    Parses the trips file from Winnipeg Transit's GTFS archive to create a
    dictionary that maps trip IDs to their respective block ID.

    :return: a dictionary in which each integer trip ID is mapped to a block
    ID (a string containing digits separated by a single dash).
    """
    TRIP_ID_COL_INDEX = 2
    BLOCK_ID_COL_INDEX = 5

    block_ids: dict[int, str] = {}

    with open(TRIPS_INPUT_FILE, "r") as file:
        file.readline() # Skip header

        for row in file:
            tokens = row.split(",")

            trip_id = int(tokens[TRIP_ID_COL_INDEX])
            block_id_raw = tokens[BLOCK_ID_COL_INDEX].strip()
            block_id = block_id_raw[block_id_raw.find("-") + 1:]

            block_ids[trip_id] = block_id # Trip IDs do not repeat themselves

    return block_ids

def get_all_arrival_times_for_all_stops() -> dict[timedelta, dict[int, list[int]]]:
    """
    Parses the stop times files from Winnipeg Transit's GTFS archive to create
    a data structure in which an arrival time and a stop can easily be mapped
    to a list of corresponding trip IDs.
    The result is a nested dictionary, in which the list of trip IDs for a
    given arrival time at a given stop can be accessed as follows:
    DICTIONARY[ARRIVAL_TIME][STOP_ID], where the arrival time is a timedelta
    object, and the stop IDs and trip IDs are integers.

    :return: a dictionary keyed by arrival times in which the values are
    dictionaries keyed by stop IDs, in which the values are lists of trip IDs.
    """
    TRIP_ID_COL_INDEX = 0
    ARRIVAL_TIME_COL_INDEX = 1
    STOP_ID_COL_INDEX = 3

    arrival_times: dict[timedelta, dict[int, list[int]]] = {}

    with open(STOP_TIMES_INPUT_FILE, "r") as file:
        file.readline() # Skip header

        for row in file:
            tokens = row.split(",")

            arrival_time = _parse_gtfs_time(tokens[ARRIVAL_TIME_COL_INDEX])
            stop_id = int(tokens[STOP_ID_COL_INDEX])
            trip_id = int(tokens[TRIP_ID_COL_INDEX])

            if arrival_time not in arrival_times:
                arrival_times[arrival_time] = {}
            if stop_id not in arrival_times[arrival_time]:
                arrival_times[arrival_time][stop_id] = []

            arrival_times[arrival_time][stop_id].append(trip_id)

    return arrival_times

def _parse_gtfs_time(raw_time: str) -> timedelta:
    """
    Takes a raw string representing a time in HH:MM:SS format (with
    after-midnight times) and converts it to a timedelta object with the
    respective amount of hours, minutes, and seconds.

    :param raw_time: the string representing a GTFS time in HH:MM:SS format.
    :return: a timedelta object containing the amount of hours, minutes, and
    seconds specified in the given string.
    """
    hours, minutes, seconds = map(int, raw_time.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
