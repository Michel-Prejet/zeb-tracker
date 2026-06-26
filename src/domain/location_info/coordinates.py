from utilities.InvariantHelper import require_not_none, require_state
from constants.app_constants import MIN_LATITUDE, MAX_LATITUDE, MIN_LONGITUDE, MAX_LONGITUDE


class Coordinates:
    """
    Represents a set of coordinates for a stop.
    """

    def __init__(self, latitude: float, longitude: float):
        require_not_none(latitude, "Latitude should not be None.")
        require_not_none(longitude, "Longitude should not be None.")

        self._latitude = latitude
        self._longitude = longitude

        self._check_coordinates()

    def _check_coordinates(self) -> None:
        require_not_none(self._latitude, "Latitude should not be None.")
        require_state(
            MIN_LATITUDE <= self._latitude <= MAX_LATITUDE,
            f"Latitude should be in the interval [{MIN_LATITUDE}, {MAX_LATITUDE}]."
        )

        require_not_none(self._longitude, "Longitude should not be None.")
        require_state(
            MIN_LONGITUDE <= self._longitude <= MAX_LONGITUDE,
            f"Longitude should be in the interval [{MIN_LONGITUDE}, {MAX_LONGITUDE}]."
        )

    @property
    def latitude(self) -> float:
        return self._latitude

    @property
    def longitude(self) -> float:
        return self._longitude