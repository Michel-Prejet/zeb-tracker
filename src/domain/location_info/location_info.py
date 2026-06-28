from datetime import timedelta, datetime
from domain.location_info.stop import Stop
from utilities.InvariantHelper import require_not_none, require_state


class LocationInfo:
    """
    Stores live location information recorded for a bus, including stop
    information; the current route, destination, and block ID; and the
    scheduled/estimated departure times. Also stores the timestamp for when
    the information was retrieved.
    """

    def __init__(
            self,
            stop: Stop,
            route: str,
            destination: str,
            block_id: str | None,
            scheduled_departure: timedelta,
            estimated_departure: timedelta,
            query_time: datetime):
        require_not_none(stop, "Stop should not be None.")
        require_not_none(route, "Route should not be None.")
        require_not_none(destination, "Destination should not be None.")
        require_not_none(block_id, "Block ID should not be None.")
        require_not_none(scheduled_departure, "Scheduled departure should not be None.")
        require_not_none(estimated_departure, "Estimated departure should be None.")
        require_not_none(query_time, "Query time should not be None.")

        self._stop = stop
        self._route = route
        self._destination = destination
        self._block_id = block_id
        self._scheduled_departure = scheduled_departure
        self._estimated_departure = estimated_departure
        self._query_time = query_time

        self._check_location_info()

    def _check_location_info(self) -> None:
        require_not_none(self._stop,"Stop should not be None.")

        require_not_none(self._route,"Route should not be None.")
        require_state(
            len(self._route) >= 1,
            "Route should not be empty or only whitespace."
        )

        require_not_none(self._destination,"Destination should not be None.")
        require_state(
            len(self._destination) >= 1,
            "Destination should not be empty or only whitespace."
        )

        if self._block_id is not None:
            require_state(
                len(self._block_id) >= 1,
                "Block ID should not be empty or only whitespace."
            )

        require_not_none(self._scheduled_departure,
                         "Scheduled departure should not be None.")
        require_not_none(self._estimated_departure,
                         "Estimated departure should not be None.")
        require_not_none(self._query_time,
                         "Query time should not be None.")

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
    def block_id(self) -> str:
        return self._block_id

    @property
    def scheduled_departure(self) -> timedelta:
        return self._scheduled_departure

    @property
    def estimated_departure(self) -> timedelta:
        return self._estimated_departure

    @property
    def query_time(self) -> datetime:
        return self._query_time


