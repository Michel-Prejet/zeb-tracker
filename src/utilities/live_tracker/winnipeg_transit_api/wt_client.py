import os
import time
from typing import Any
import requests
from requests import Timeout, ConnectionError, HTTPError, RequestException
from constants.app_constants import MIN_STOP_ID, MAX_STOP_ID
from utilities.invariant_helper import require_not_none, require_state
from dotenv import load_dotenv
from utilities.live_tracker.time_helper import parse_api_time
from utilities.live_tracker.winnipeg_transit_api.exceptions.transit_api_error import MissingAPIKeyError, WtAuthError, \
    WtTimeoutError, WtConnectionError, WtHTTPError, WtResponseError, WtAPIError, WtParsingError

load_dotenv()


WT_API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.winnipegtransit.com/v4"
REQUEST_DELAY = 0.2
REQUEST_DELAY_ON_429 = 5

def get_stop_information_and_schedule(stop_number: int) -> dict:
    """
    Sends a request to the Winnipeg Transit API to retrieve information
    about the stop with the given 5-digit ID and parses the retrieved data,
    raising custom exceptions if any errors occur related to the API key,
    the request, or the data parsing.

    :param stop_number: the 5-digit ID of the stop for which to retrieve
    information from the Winnipeg Transit API.
    :return: a dictionary containing the stop ID ("id"), the stop name ("name"),
    the stop's coordinates ("coordinates"), and a list of upcoming arrivals
    sorted by increasing estimated arrival time ("buses").
    """
    require_not_none(stop_number, "Stop number should not be None.")
    require_state(
    MIN_STOP_ID <= stop_number <= MAX_STOP_ID,
    f"Stop number should be a 5-digit integer."
    )

    if WT_API_KEY is None:
        raise MissingAPIKeyError()

    url = f"{BASE_URL}/stops/{stop_number}/schedule.json"
    params = {
        "api-key": WT_API_KEY,
    }

    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = _parse_raw_stop_data(response.json())
    except Timeout:
        raise WtTimeoutError()
    except ConnectionError:
        raise WtConnectionError()
    except HTTPError as e:
        if e.response.status_code == 401:
            raise WtAuthError(401)
        elif e.response.status_code == 429:
            time.sleep(REQUEST_DELAY_ON_429)
        else:
            raise WtHTTPError(e.response.status_code)
    except ValueError:
        raise WtResponseError()
    except RequestException:
        raise WtAPIError()

    return data

def _parse_raw_stop_data(raw_data: dict) -> dict:
    """
    Parses raw stop data from the Winnipeg Transit API. Extracts the stop's
    name, ID, and coordinates, as well as its schedule.

    :param raw_data: the raw stop data from the Winnipeg Transit API to parse.
    :return: a dictionary containing the stop ID ("id"), the stop name ("name"),
    the stop's coordinates ("coordinates"), and a list of upcoming arrivals
    sorted by increasing estimated departure time ("buses").
    """
    stop_schedule = _try_key(raw_data, "stop-schedule")
    stop = _try_key(stop_schedule, "stop")

    # Get stop ID and stop name
    try:
        stop_id = int(_try_key(stop, "key"))
    except (ValueError, TypeError):
        raise WtParsingError("key", stop)
    stop_name = _try_key(stop, "name")

    # Get stop latitude and longitude
    centre = _try_key(stop, "centre")
    geographic = _try_key(centre, "geographic")
    try:
        latitude = float(_try_key(geographic, "latitude"))
    except (ValueError, TypeError):
        raise WtParsingError("latitude", geographic)
    try:
        longitude = float(_try_key(geographic, "longitude"))
    except (ValueError, TypeError):
        raise WtParsingError("longitude", geographic)

    # Get the list of arrivals
    route_schedules = _try_key(stop_schedule, "route-schedules")
    if not isinstance(route_schedules, list):
        raise WtParsingError("route-schedules", stop_schedule)
    bus_arrivals = _parse_raw_schedule(route_schedules)

    return {
        "id": stop_id,
        "name": stop_name,
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude
        },
        "buses": bus_arrivals
    }

def _parse_raw_schedule(raw_data: list[dict]) -> list[dict]:
    """
    Parses a raw list of bus arrivals at a stop from the Winnipeg Transit API.
    For each arrival, extracts the route name, the tracking number of the bus,
    the destination, and the scheduled/estimated departure times.

    :param raw_data: the raw schedule from the Winnipeg Transit API to parse.
    :return: a list of dictionaries, each of which contains information for an
    arrival at the stop. The list is sorted by increasing estimated departure time.
    """
    bus_arrivals: list[dict] = []

    for schedule in raw_data:
        # Get the route name
        route = _try_key(schedule, "route")
        route_name = _try_key(route, "key")

        # Get the buses arriving at the stop
        scheduled_stops = _try_key(schedule, "scheduled-stops")
        for arrival in scheduled_stops:
            arrival = _parse_raw_arrival_data(arrival, route_name)
            if arrival is not None:
                bus_arrivals.append(arrival)

    bus_arrivals.sort(
        key=lambda b: parse_api_time(b["departures"]["estimated"])
    )

    return bus_arrivals

def _parse_raw_arrival_data(raw_data: dict, route_name: str) -> dict | None:
    """
    Parses raw arrival data from the Winnipeg Transit API for a bus at a stop.
    Extracts the tracking number of the bus, the route, the destination, and the
    scheduled/estimated departure times.

    :param raw_data: the raw arrival data from the Winnipeg Transit API to parse.
    :param route_name: the name of the route under which the given data was found.
    :return: a dictionary containing the tracking number of the bus ("tracking_num"),
    the route ("route"), the destination ("destination"), and the scheduled/estimated
    departure times ("departures"); or None if the bus is cancelled or not
    assigned.
    """
    # Return None if the bus is cancelled
    cancelled = _try_key(raw_data, "cancelled")
    if cancelled == "true":
        return None

    # Get bus tracking number
    bus = raw_data.get("bus")
    if bus is None:
        return None

    try:
        tracking_num = int(_try_key(bus, "key"))
    except (ValueError, TypeError):
        raise WtParsingError("key", bus)

    # Get estimated and scheduled departure times
    times = _try_key(raw_data, "times")
    departure = _try_key(times, "departure")
    scheduled_departure = _try_key(departure, "scheduled")
    estimated_departure = _try_key(departure, "estimated")

    # Get destination
    variant = _try_key(raw_data, "variant")
    destination = _try_key(variant, "name")

    return {
        "tracking_num": tracking_num,
        "route": route_name,
        "destination": destination,
        "departures": {
            "scheduled": scheduled_departure,
            "estimated": estimated_departure,
        }
    }

def _try_key(data: dict, key: str) -> Any:
    """
    Attempts to access the entry in the given dictionary with the
    given key. If successful, the entry is returned, otherwise a DataParsingError
    is raised with the name of the attribute.

    :param data: the dictionary in which to attempt to access an entry.
    :param key: the key for the entry to access in the given dictionary.
    :return: the entry at the given key in the given dictionary.
    """
    value = data.get(key)
    if value is None:
        raise WtParsingError(key, data)
    return value

