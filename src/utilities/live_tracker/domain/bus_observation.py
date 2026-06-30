from datetime import timedelta
from constants.app_constants import MIN_BUS_TRACKING_NUM, MAX_BUS_TRACKING_NUM
from utilities.invariant_helper import require_not_none, require_state
from utilities.live_tracker.domain.stop import Stop


class BusObservation:
    """
    Represents an observation of a bus at a stop. Stores static stop information
    as well as the bus's route, destination, tracking number, and
    scheduled/estimated departure times from the stop.
    """

    def __init__(self, stop: Stop, route: str, destination: str, tracking_num: int,
                 scheduled_departure: timedelta, estimated_departure: timedelta):
        require_not_none(stop, "Stop should not be None.")
        require_not_none(route, "Route should not be None.")
        require_not_none(destination, "Destination should not be None.")
        require_not_none(tracking_num, "Tracking number should not be None.")
        require_not_none(scheduled_departure, "Scheduled departure should not be None.")
        require_not_none(estimated_departure, "Estimated departure should not be None.")

        self._stop = stop
        self._route = route
        self._destination = destination
        self._tracking_num = tracking_num
        self._scheduled_departure = scheduled_departure
        self._estimated_departure = estimated_departure

        self._check_bus_observation()

    def _check_bus_observation(self) -> None:
        require_not_none(
            self._stop,
            "Stop for bus observation should not be None."
        )

        require_not_none(
            self._route,
            "Route for bus observation should not be None."
        )
        require_state(
            len(self._route) >= 1,
            "Route for bus observation should not be empty or "
                     "only whitespace."
        )

        require_not_none(
            self._destination,
            "Destination for bus observation should not be None."
        )
        require_state(
            len(self._destination) >= 1,
            "Destination for bus observation should not be empty or "
                     "only whitespace."
        )

        require_not_none(
            self._tracking_num,
            "Tracking number for bus observation should not be None."
        )
        require_state(
            MIN_BUS_TRACKING_NUM <= self._tracking_num <= MAX_BUS_TRACKING_NUM,
            f"Tracking number for bus observation should be a 3-digit integer.")

        require_not_none(
            self._scheduled_departure,
            "Scheduled departure for bus observation should not be None."
        )

        require_not_none(
            self._estimated_departure,
            "Estimated departure for bus observation should not be None."
        )

    def __eq__(self, other) -> bool:
        """
        Determines whether a given bus observation is equal to this bus
        observation. Two bus observations are equal if they have the same
        stop, tracking number, and scheduled departure time.
        """
        return (
                isinstance(other, BusObservation)
                and self._stop == other._stop
                and self._tracking_num == other._tracking_num
                and self._scheduled_departure == other._scheduled_departure
        )

    @property
    def stop(self) -> Stop:
        return self._stop

    @property
    def route(self) -> str:
        return self._route

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def tracking_num(self) -> int:
        return self._tracking_num

    @property
    def scheduled_departure(self) -> timedelta:
        return self._scheduled_departure

    @property
    def estimated_departure(self) -> timedelta:
        return self._estimated_departure

