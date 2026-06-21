from datetime import datetime
from domain.Fleet import Fleet
from domain.location_info.LocationInfo import LocationInfo
from domain.location_info.Stop import Stop
from utilities.live_tracker.LiveBusTracker import LiveBusTracker
from utilities.live_tracker.domain.Coordinates import Coordinates


def update_bus_locations(fleet: Fleet, tracker: LiveBusTracker):
    """
    Updates the location info attribute of each bus in the given fleet using
    the given tracker. Assumes that stops have already been scanned in the
    tracker. Converts location information dictionaries to LocationInfo objects
    before assigning them to the buses.

    :param fleet: the fleet in which to update the location information of
    all buses.
    :param tracker: the live tracker utility used to retrieve location information.
    """

    for bus in fleet.sorted_buses():
        location_info = tracker.get_location_info_for_bus(bus.tracking_num)
        if location_info is not None:
            bus.location_info = _create_location_info_record_from_dict(location_info)

def _create_location_info_record_from_dict(location_info_raw: dict) -> LocationInfo:
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
    stop_id: int = location_info_raw["stop"]["id"]
    stop_name = location_info_raw["stop"]["name"]
    stop_latitude: float = location_info_raw["stop"]["coordinates"]["latitude"]
    stop_longitude: float = location_info_raw["stop"]["coordinates"]["longitude"]
    route = location_info_raw["route"]
    destination = location_info_raw["destination"]
    scheduled_departure = location_info_raw["departures"]["scheduled"]
    estimated_departure = location_info_raw["departures"]["estimated"]
    block_id = location_info_raw.get("block_id")
    query_time = datetime.fromisoformat(location_info_raw.get("query_time"))

    stop = Stop(stop_name, stop_id, Coordinates(stop_latitude, stop_longitude))
    return LocationInfo(stop, route, destination, block_id, scheduled_departure, estimated_departure, query_time)
