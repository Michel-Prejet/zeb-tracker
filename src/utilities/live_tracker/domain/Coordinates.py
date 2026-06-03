from utilities.InvariantHelper import require_not_none, require_state

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

class Coordinates:
    """
    Represents a set of coordinates for a stop.
    """

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

        self._check_coordinates()

    def _check_coordinates(self) -> None:
        require_not_none(self.latitude, "Latitude should not be None.")
        require_not_none(self.longitude, "Longitude should not be None.")
        require_state(MIN_LATITUDE <= self.latitude <= MAX_LATITUDE,
                      f"Latitude should be in the interval [{MIN_LATITUDE}, {MAX_LATITUDE}].")
        require_state(MIN_LONGITUDE <= self.longitude <= MAX_LONGITUDE,
                      f"Longitude should be in the interval [{MIN_LONGITUDE}, {MAX_LONGITUDE}].")
