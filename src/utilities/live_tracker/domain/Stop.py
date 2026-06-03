from utilities.InvariantHelper import require_not_none, require_state
from utilities.live_tracker.domain.Coordinates import Coordinates

STOP_NUMBER_LENGTH = 5


class Stop:
    """
    Static information for a stop read from the Winnipeg Transit API, including
    the stop's name, 5-digit ID, and coordinates.
    """

    def __init__(self, name: str, stop_id: int, coordinates: Coordinates):
        self.name = name
        self.stop_id = stop_id
        self.coordinates = coordinates

        self._check_stop()

    def __eq__(self, other) -> bool:
        """
        Determines whether a given stop is equal to this stop. Two stops
        are equal if they have the same 5-digit stop ID.

        :param other: the stop to check for equality.
        :return: True if `other` has the same stop ID as this stop; False
        otherwise.
        """
        require_not_none(other, "Stop to check for equality should not be None.")

        return self.stop_id == other.stop_id

    def _check_stop(self) -> None:
        require_not_none(self.name, "Stop name should not be None.")
        require_state(len(self.name) >= 1,
                      "Stop name should not be empty or only whitespace.")
        require_not_none(self.stop_id, "Stop ID should not be None.")
        require_state(len(str(self.stop_id)) == STOP_NUMBER_LENGTH,
                      f"Stop ID should contain exactly {STOP_NUMBER_LENGTH} digits.")
        require_not_none(self.coordinates, "Stop coordinates should not be None.")