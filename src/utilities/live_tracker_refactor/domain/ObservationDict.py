from utilities.InvariantHelper import require_not_none, require_state
from utilities.live_tracker_refactor.domain.BusObservation import BusObservation
import bisect


class ObservationDict:
    """
    Dictionary mapping bus tracking numbers to a list of observations recorded
    for that bus. The lists of observations are sorted by increasing estimated
    departure time.
    """

    def __init__(self):
        self.bus_observations: dict[int, list[BusObservation]] = {}

    def get_all_observations_for_bus(self, bus_tracking_num: int) -> list[BusObservation]:
        """
        :param bus_tracking_num: the tracking number of the bus for which to
        retrieve all observations.
        :return: a list of observations for the given bus (may be empty if
        no such bus was found).
        """
        if bus_tracking_num in self.bus_observations:
            return self.bus_observations[bus_tracking_num]
        return []

    def get_earliest_observation_for_bus(self, bus_tracking_num: int) -> BusObservation | None:
        """
        :param bus_tracking_num: the tracking number of the bus for which to
        retrieve the observation with the earliest estimated departure time.
        :return: the observation with the earliest departure time for the given
        bus, or None if no observations were found for that tracking number.
        """
        all_observations = self.get_all_observations_for_bus(bus_tracking_num)
        if all_observations:
            return all_observations[0]
        return None

    def add_observation(self, observation: BusObservation) -> None:
        """
        Adds a given observation to the dictionary. The bus tracking number
        stored in the observation is used as the key, and the observation
        is added to the associated list, maintaining order so that the list
        is sorted by increasing estimated departure time.
        Assumes that no observation has already been added with the same
        tracking number, stop ID, and scheduled departure time.

        :param observation: the observation to add to this observation dictionary.
        """
        require_not_none(observation, "Observation to add should not be None.")

        tracking_num = observation.tracking_num
        if tracking_num not in self.bus_observations:
            self.bus_observations[tracking_num] = []

        require_state(observation not in self.bus_observations[tracking_num],
                      "Observation should not have already been added to the dictionary.")

        bisect.insort(self.bus_observations[tracking_num], observation,
                      key=lambda obs: obs.estimated_departure)
