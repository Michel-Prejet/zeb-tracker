from datetime import datetime
from domain.fleet import Fleet
from domain.location_info.location_info import LocationInfo
from domain.location_info.stop import Stop
from utilities.invariant_helper import require_not_none
from utilities.live_tracker.live_bus_tracker import LiveBusTracker
from utilities.live_tracker.domain.coordinates import Coordinates


def update_bus_locations(fleet: Fleet, tracker: LiveBusTracker) -> None:
    """
    Updates the location info attribute of each bus in the given fleet using
    the given tracker. Assumes that stops have already been scanned in the
    tracker. Any stale location info from past scans is cleared from the fleet.

    :param fleet: the fleet in which to update the location information of
    all buses.
    :param tracker: the live tracker utility used to retrieve location information.
    """
    require_not_none(fleet, "Fleet should not be None.")
    require_not_none(tracker, "Live bus tracker should not be None.")

    for bus in fleet.buses:
        location_info = tracker.get_location_info_for_bus(bus.tracking_num)

        if location_info is not None:
            fleet.set_bus_location_info(
                bus.tracking_num,
                _create_location_info_from_raw(location_info),
                notify=False
            )
        else:
            fleet.reset_bus_location_info(bus.tracking_num, notify=False)

    fleet.notify_all()

def _create_location_info_from_raw(location_info_raw: dict) -> LocationInfo:
    """
    Creates a LocationInfo object from a dictionary containing location information
    for a bus. Assumes that the data in the dictionary is properly structured
    and formatted. It should include the stop ID, name, and coordinates; the
    route and destination; the scheduled and estimated departure times as
    strings of the form HH:MM:SS; the query time; and, optionally, a block ID.

    :param location_info_raw: a dictionary containing location information
    for a bus.
    :return: a LocationInfo object containing the given information.
    """
    require_not_none(location_info_raw, "Location info should not be None.")

    stop_id: int = location_info_raw["stop"]["id"]
    stop_name = location_info_raw["stop"]["name"]
    stop_latitude: float = location_info_raw["stop"]["coordinates"]["latitude"]
    stop_longitude: float = location_info_raw["stop"]["coordinates"]["longitude"]
    route = location_info_raw["route"]
    destination = location_info_raw["destination"]
    scheduled_departure = location_info_raw["departures"]["scheduled"]
    estimated_departure = location_info_raw["departures"]["estimated"]
    block_id = location_info_raw.get("block_id")
    query_time = datetime.fromisoformat(location_info_raw["query_time"])

    stop = Stop(stop_name, stop_id, Coordinates(stop_latitude, stop_longitude))

    return LocationInfo(
        stop,
        route,
        destination,
        block_id,
        scheduled_departure,
        estimated_departure,
        query_time
    )
