from utilities.InvariantHelper import require_not_none, require_state
from utilities.live_tracker.domain.Coordinates import Coordinates
from constants.app_constants import MIN_STOP_ID, MAX_STOP_ID


class Stop:
    """
    Stores information for a stop including its name, 5-digit ID, and
    coordinates.
    """

    def __init__(self, name: str, stop_id: int, coordinates: Coordinates):
        require_not_none(name, "Stop name should not be None.")
        require_not_none(stop_id, "Stop ID should not be None.")
        require_not_none(coordinates, "Stop coordinates should not be None.")

        self._name = name
        self._stop_id = stop_id
        self._coordinates = coordinates

        self._check_stop()

    def _check_stop(self) -> None:
        require_not_none(self._name, "Stop name should not be None.")
        require_state(
            len(self._name) >= 1,
            "Stop name should not be empty or only whitespace."
        )

        require_not_none(self._stop_id, "Stop ID should not be None.")
        require_state(
            MIN_STOP_ID <= self._stop_id <= MAX_STOP_ID,
            f"Stop ID should be a 5-digit integer."
        )

        require_not_none(
            self._coordinates,
            "Stop coordinates should not be None."
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def stop_id(self) -> int:
        return self._stop_id

    @property
    def coordinates(self) -> Coordinates:
        return self._coordinates