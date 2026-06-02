from utilities.InvariantHelper import require_not_none, require_state
from utilities.live_tracker_refactor.domain.BusObservation import BusObservation
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.GTFSReader import GTFSReader
from utilities.live_tracker_refactor.winnipeg_transit_gtfs.exceptions.TransitGTFSError import DepartureTimeNotFoundError, \
    StopNotFoundError, TripIDNotFoundError


class BlockIDFinder:
    """
    Uses a GTFS reader to infer the block ID for a bus based on a list of
    observations recorded for that bus.
    """

    def __init__(self, gtfs_reader: GTFSReader):
        self.gtfs = gtfs_reader

    def infer_block_id_from_gtfs(self, observations: list[BusObservation]) -> str | None:
        """
        Uses GTFS data to infer the block ID based on a given list of observations
        for a bus, using the stop ID and scheduled departure time stored in each
        observation. Retrieves the list of trip IDs corresponding to each
        stop ID/scheduled departure time pair, converts them to block IDs, and
        counts the most commonly occurring block ID overall.

        :param observations: a list of observations for a given bus, from which
        to infer the block ID.
        :return: the block ID inferred from the given list, or None if no block
        ID occurred at least 3 times.
        """
        require_not_none(observations, "Observation list should not be None.")
        for obs in observations:
            require_not_none(obs, "Observation in list should not be None.")
        require_state(len(observations) >= 1,
                      "Observation list should not be empty.")

        MIN_NUM_BLOCK_ID_OCCURRENCES_FOR_INFERENCE = 3

        block_id_counts: dict[str, int] = {}

        for obs in observations:
            stop_id = obs.stop.stop_id
            scheduled_departure_time = obs.scheduled_departure

            try:
                trip_ids = self.gtfs.get_trip_ids(stop_id, scheduled_departure_time)
            except (StopNotFoundError, DepartureTimeNotFoundError):
                continue

            for trip_id in trip_ids:
                try:
                    block_id = self.gtfs.get_block_id(trip_id)
                except TripIDNotFoundError:
                    continue

                block_id_counts[block_id] = block_id_counts.get(block_id, 0) + 1

        if not block_id_counts:
            return None

        most_common_block_id = max(block_id_counts, key=block_id_counts.get)
        max_number_occurrences = block_id_counts[most_common_block_id]

        if max_number_occurrences < MIN_NUM_BLOCK_ID_OCCURRENCES_FOR_INFERENCE:
            return None

        return most_common_block_id

