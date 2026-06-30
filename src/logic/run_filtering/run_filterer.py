from datetime import date
from typing import Callable
from domain.run_assignment import RunAssignment
from logic.run_filtering.run_filter_type import RunFilterType
from utilities.invariant_helper import require_not_none, require_state


def build_search_filter_function(filter_input: str | tuple[date, date],
                                 filter_type: RunFilterType) -> Callable:
    """
    Creates a function that filters a list of run assignments based on the
    given filter type and input.
    """
    require_not_none(filter_input, "Filter input should not be None.")
    require_not_none(filter_type, "Filter type should not be None.")

    def filter_function(assigned_run_list: list[RunAssignment]) -> list[RunAssignment]:
        _require_valid_run_assignment_list(assigned_run_list)

        new_list = assigned_run_list.copy()

        if filter_type == RunFilterType.DATE:
            require_state(
                isinstance(filter_input, tuple),
                "Filter input should be a tuple when filtering by date."
            )

            start_date, end_date = filter_input
            new_list = FILTER_ACTIONS[filter_type](new_list, start_date, end_date)
        elif filter_input:
            require_state(
                isinstance(filter_input, str),
                "Filter input should be a string when not filtering by date."
            )

            new_list = FILTER_ACTIONS[filter_type](new_list, filter_input)

        return new_list

    return filter_function

def _filter_by_date_range(assigned_run_list: list[RunAssignment],
                          start_date: date, end_date: date) -> list[RunAssignment]:
    """
    Filters the given list of run assignments by the given date range. Any run
    whose date is between the given start and end dates (inclusive) is included
    in the returned list.
    """
    _require_valid_run_assignment_list(assigned_run_list)
    require_not_none(start_date, "Start date should not be None.")
    require_not_none(end_date, "End date should not be None.")

    return [
        assignment
        for assignment in assigned_run_list
        if start_date <= assignment.date <= end_date
    ]

def _filter_by_block_id(assigned_run_list: list[RunAssignment],
                        block_id: str) -> list[RunAssignment]:
    """
    Filters the given list of run assignments by the given block ID. Any run
    with the same block ID as the given block ID is included in the returned
    list.
    """
    _require_valid_run_assignment_list(assigned_run_list)
    require_not_none(block_id, "Block ID should not be None.")

    return [
        assignment
        for assignment in assigned_run_list
        if block_id == assignment.block_id
    ]

def _filter_by_bus_tracking_num(assigned_run_list: list[RunAssignment],
                                tracking_num: str) -> list[RunAssignment]:
    """
    Filters the given list of run assignments by the given tracking number. Any
    run whose associated bus's tracking number contains the given tracking
    number as a substring is included in the returned list.
    """
    _require_valid_run_assignment_list(assigned_run_list)
    require_not_none(tracking_num, "Tracking number should not be None.")

    return [
        assignment
        for assignment in assigned_run_list
        if tracking_num in str(assignment.tracking_num)
    ]

def _filter_by_bus_model(assigned_run_list: list[RunAssignment],
                         model: str) -> list[RunAssignment]:
    """
    Filters the given list of run assignments by the given model. Any run whose
    associated bus's model contains the given model as a substring is included
    in the returned list.
    """
    _require_valid_run_assignment_list(assigned_run_list)
    require_not_none(model, "Model should not be None.")

    return [
        assignment
        for assignment in assigned_run_list
        if model in assignment.bus.model
    ]

def _require_valid_run_assignment_list(assigned_run_list: list[RunAssignment]) -> None:
    require_not_none(assigned_run_list, "Run assignment list should not be None.")
    for assigned_run in assigned_run_list:
        require_not_none(assigned_run, "Run assignment in list should not be None.")

FILTER_ACTIONS = {
    RunFilterType.DATE: _filter_by_date_range,
    RunFilterType.BLOCK_ID: _filter_by_block_id,
    RunFilterType.BUS_TRACKING_NUM: _filter_by_bus_tracking_num,
    RunFilterType.BUS_MODEL: _filter_by_bus_model
}

