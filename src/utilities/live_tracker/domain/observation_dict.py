from utilities.invariant_helper import require_not_none, require_state
from utilities.live_tracker.time_helper import get_curr_time_as_timedelta
from utilities.live_tracker.domain.bus_observation import BusObservation
import bisect


class ObservationDict:
    """
    Maps bus tracking numbers to a list of observations recorded for that bus.
    The lists of observations are sorted by increasing estimated departure time.
    """

    def __init__(self):
        self.bus_observations: dict[int, list[BusObservation]] = {}

    def get_all_observations_for_bus(self, bus_tracking_num: int) -> list[BusObservation]:
        """
        Retrieves a list of observations for the bus with the given tracking
        number.
        """
        require_not_none(bus_tracking_num, "Bus tracking number should not be None.")

        if bus_tracking_num in self.bus_observations:
            return self.bus_observations[bus_tracking_num]
        return []

    def get_most_current_observation_for_bus(self, bus_tracking_num: int) -> BusObservation | None:
        """
        Retrieves the observation with the earliest departure time that is greater
        than the current time for the given bus, or returns None if no observations
        were found for that tracking number.
        """
        require_not_none(bus_tracking_num, "Bus tracking number should not be None.")

        all_observations = self.get_all_observations_for_bus(bus_tracking_num)

        if all_observations:
            curr_time = get_curr_time_as_timedelta()

            for obs in all_observations:
                if obs.estimated_departure >= curr_time:
                    return obs

            return all_observations[-1]

        return None

    def add_observation(self, observation: BusObservation) -> None:
        """
        Adds a given observation to the dictionary. The bus tracking number
        stored in the observation is used as the key, and the observation
        is added to the associated list, maintaining order so that the list
        is sorted by increasing estimated departure time.
        Assumes that no observation has already been added with the same
        tracking number, stop ID, and scheduled departure time.
        """
        require_not_none(observation, "Observation to add should not be None.")

        tracking_num = observation.tracking_num
        if tracking_num not in self.bus_observations:
            self.bus_observations[tracking_num] = []

        require_state(
            observation not in self.bus_observations[tracking_num],
            "Observation should not have already been added to the dictionary."
        )

        bisect.insort(
            self.bus_observations[tracking_num],
            observation,
            key=lambda obs: obs.estimated_departure
        )
