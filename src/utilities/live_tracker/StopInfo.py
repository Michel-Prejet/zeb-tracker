import requests
from utilities.InvariantHelper import require_not_none, require_state
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.winnipegtransit.com/v4"

STOP_NUMBER_LENGTH = 5

def get_stop_info(stop_number: int) -> dict:
    """
    Creates a customized dictionary for the stop with the given number by
    querying the Winnipeg Transit API.

    :param stop_number: the 5-digit ID of the stop for which to retrieve
    information.
    :return: a dictionary containing the name, latitude, and longitude of the
    stop, as well as an array in which each element is a dictionary containing
    the tracking number, the ETA, and the destination of a bus at the stop.
    """
    require_not_none(stop_number, "Stop number should not be None.")
    require_state(len(str(stop_number)) == STOP_NUMBER_LENGTH,
                  f"Stop number should contain exactly {STOP_NUMBER_LENGTH} digits.")

    data = _get_stop_info_raw(stop_number)["stop-schedule"]

    name = data["stop"]["name"]
    latitude = float(data["stop"]["centre"]["geographic"]["latitude"])
    longitude = float(data["stop"]["centre"]["geographic"]["longitude"])
    buses = _create_bus_info_list_from_raw_data(data)

    return {
        "id": stop_number,
        "name": name,
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude
        },
        "buses": buses
    }

def _create_bus_info_list_from_raw_data(schedule: dict) -> list[dict]:
    """
    Creates a list of dictionaries, each of which contains relevant information
    about a bus arriving at a stop corresponding to a given schedule.

    :param schedule: the raw stop schedule data from the Winnipeg Transit API.
    :return: a list of dictionaries, each of which contains the tracking number,
    estimated arrival time, route, and destination for a bus arriving at the
    stop.
    """
    buses = []

    schedule = schedule["route-schedules"]
    for route in schedule:
        route_name = str(route["route"]["number"])

        for bus in route["scheduled-stops"]:
            if bus["cancelled"] == "false":
                bus_entry = _create_bus_entry_from_raw_data(bus, route_name)
                if bus_entry is not None:
                    buses.append(bus_entry)

    buses.sort(key=lambda b: datetime.fromisoformat(b["arrival_time_est"]))

    return buses

def _create_bus_entry_from_raw_data(bus_data: dict, route_name: str) -> dict | None:
    """
    Creates a dictionary containing only relevant information about a bus
    arriving at a stop.

    :param bus_data: raw scheduled stop element from the Winnipeg Transit API.
    :param route_name: the name of the route under which the bus information
    is listed.
    :return: a dictionary containing the tracking number, the estimated arrival
    time, the route, and the destination of the bus at the stop, or None if the
    API fails to return one of those elements.
    """
    bus = bus_data.get("bus")
    if bus is None:
        return None

    tracking_num_raw = bus.get("key")
    if tracking_num_raw is None:
        return None

    times = bus_data.get("times")
    if times is None:
        return None
    arrival = times.get("arrival")
    if arrival is None:
        return None
    arrival_time_scheduled = arrival.get("scheduled")
    arrival_time_est = arrival.get("estimated") or arrival.get("scheduled")

    variant = bus_data.get("variant")
    if variant is None:
        return None
    destination = variant.get("name")

    return {
        "tracking_num": int(tracking_num_raw),
        "arrival_time_scheduled": arrival_time_scheduled,
        "arrival_time_est": arrival_time_est,
        "route": route_name,
        "destination": destination,
    }

def _get_stop_info_raw(stop_number: int) -> dict:
    """
    :param stop_number: the 5-digit ID of the stop for which to retrieve
    information from the Winnipeg Transit API.
    :return: a dictionary containing properties and schedule information
    for the given stop.
    """
    require_not_none(stop_number, "Stop number should not be None.")
    require_state(len(str(stop_number)) == STOP_NUMBER_LENGTH,
                  f"Stop number should contain exactly {STOP_NUMBER_LENGTH} digits.")

    url = f"{BASE_URL}/stops/{stop_number}/schedule.json"
    params = {
        "api-key": API_KEY,
    }

    return requests.get(url, params=params).json()


