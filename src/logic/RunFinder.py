from domain.InferredRunList import InferredRunList
from domain.Run import Run


def infer_runs_from_location_info(runs: InferredRunList) -> None:
    """
    Populates a given inferred run list based on the location information
    for buses in the fleet associated with that list. Creates runs from the
    block ID and run date, then adds them to the inferred run list.

    :param runs: the inferred run list to populate.
    """
    for bus in runs.fleet.sorted_buses():
        if (bus.location_info is not None and
                bus.location_info.block_id is not None):
            run = Run(bus.location_info.block_id, bus.location_info.query_time.date())
            runs.add(bus.tracking_num, run)
