from domain.inferred_run_list import InferredRunList
from domain.run import Run
from domain.run_assignment import RunAssignment
from utilities.invariant_helper import require_not_none


def infer_runs_from_location_info(runs: InferredRunList) -> None:
    """
    Populates a given inferred run list based on the location information
    for buses in the fleet associated with that list. Creates runs from the
    block ID and run date, then adds them to the inferred run list.

    :param runs: the inferred run list to populate.
    """
    require_not_none(runs, "Inferred run list should not be None.")

    for bus in runs.buses:
        if (bus.location_info is not None
            and bus.location_info.block_id is not None):
            run = Run(bus.location_info.block_id, bus.location_info.query_time.date())

            runs.add_inferred_run(RunAssignment(run, bus))
