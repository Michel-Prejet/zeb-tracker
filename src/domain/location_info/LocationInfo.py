from datetime import timedelta
from domain.location_info.Stop import Stop
from utilities.InvariantHelper import require_not_none, require_state


class LocationInfo:
    """
    Stores live location information recorded for a bus, including stop
    information; the current route, destination, and block ID; and the
    scheduled/estimated departure times.
    """

    def __init__(self, stop: Stop, route: str, destination: str, block_id: str | None,
                 scheduled_departure: timedelta, estimated_departure: timedelta):
        self.stop = stop
        self.route = route
        self.destination = destination
        self.block_id = block_id
        self.scheduled_departure = scheduled_departure
        self.estimated_departure = estimated_departure

        self._check_location_info()

    def _check_location_info(self) -> None:
        require_not_none(self.stop,"Stop should not be None.")
        require_not_none(self.route,"Route should not be None.")
        require_state(len(self.route) >= 1, "Route should not be empty.")
        require_not_none(self.destination,"Destination should not be None.")
        require_state(len(self.destination) >= 1, "Destination should not be empty.")
        if self.block_id is not None:
            require_state(len(self.block_id) >= 1, "Block ID should not be empty.")
        require_not_none(self.scheduled_departure, "Scheduled departure should not be None.")
        require_not_none(self.estimated_departure, "Estimated departure should not be None.")
