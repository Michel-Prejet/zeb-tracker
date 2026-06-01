from datetime import timedelta
from utilities.InvariantHelper import require_not_none, require_state
from utilities.live_tracker_refactor.domain.Stop import Stop


BUS_TRACKING_NUM_LENGTH = 3

class BusObservation:
    """
    Represents an observation of a bus at a stop in the Winnipeg Transit API.
    Stores static information about the stop as well as bus's route, destination,
    tracking number, and scheduled/estimated arrival times at the stop.
    """

    def __init__(self, stop: Stop, route: str, destination: str, tracking_num: int,
                 scheduled_arrival: timedelta, estimated_arrival: timedelta):
        self.stop = stop
        self.route = route
        self.destination = destination
        self.tracking_num = tracking_num
        self.scheduled_arrival = scheduled_arrival
        self.estimated_arrival = estimated_arrival

        self._check_bus_observation()

    def __eq__(self, other) -> bool:
        """
        Determines whether a given bus observation is equal to this bus
        observation. Two bus observations are equal if they have the same stop,
        tracking number, and scheduled arrival time.

        :param other: the bus observation to check for equality.
        :return: True if `other` has the same stop, tracking number, and scheduled
        arrival time as this stop; False otherwise.
        """

        require_not_none(other,
                         "Bus observation to check for equality should not be None.")

        return (self.stop == other.stop and self.tracking_num == other.tracking_num
                and self.scheduled_arrival == other.scheduled_arrival)

    def _check_bus_observation(self) -> None:
        require_not_none(self.stop,
                         "Stop for bus observation should not be None.")
        require_not_none(self.route,
                         "Route for bus observation should not be None.")
        require_state(len(self.route) >= 1,
                      "Route for bus observation should not be empty or "
                      "only whitespace.")
        require_not_none(self.destination,
                         "Destination for bus observation should not be None.")
        require_state(len(self.destination) >= 1,
                      "Destination for bus observation should not be empty or "
                      "only whitespace.")
        require_not_none(self.tracking_num,
                         "Tracking number for bus observation should not be None.")
        require_state(len(str(self.tracking_num)) == BUS_TRACKING_NUM_LENGTH,
                      f"Tracking number for bus observation should contain exactly "
                      f"{BUS_TRACKING_NUM_LENGTH} digits.")
        require_not_none(self.scheduled_arrival,
                         "Scheduled arrival for bus observation should not be None.")
        require_not_none(self.estimated_arrival,
                         "Estimated arrival for bus observation should not be None.")

