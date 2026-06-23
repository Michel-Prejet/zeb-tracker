from datetime import date
from typing import Callable
from domain.bus import Bus
from domain.run import Run
from logic.RunFiltering.RunFilterType import RunFilterType


def build_search_filter_function(filter: str | tuple[date, date], filter_type: RunFilterType) -> Callable:
    """
    :param filter: the string or date range used to filter runs.
    :param filter_type: the type of filter to apply to the run list.
    :return: a function that filters a list of RUN, BUS tuples based on the
    given parameters.
    """
    def filter_function(run_list: list[tuple[Run, Bus]]) -> list[tuple[Run, Bus]]:
        new_list = run_list.copy()

        if filter_type == RunFilterType.DATE:
            start_date, end_date = filter
            new_list = FILTER_ACTIONS[filter_type](new_list, start_date, end_date)
        elif len(filter) > 0:
            new_list = FILTER_ACTIONS[filter_type](new_list, filter)

        return new_list

    return filter_function

def _filter_by_date_range(run_list: list[tuple[Run, Bus]], start_date: date, end_date: date) -> list[tuple[Run, Bus]]:
    """
    Filters the given list of RUN, BUS tuples by the given date range. Any run
    whose date is between the given start and end dates (inclusive) is included
    in the returned list.
    """
    filtered_list: list[tuple[Run, Bus]] = []

    for entry in run_list:
        run = entry[0]

        if start_date <= run.run_date <= end_date:
            filtered_list.append(entry)

    return filtered_list

def _filter_by_block_id(run_list: list[tuple[Run, Bus]], block_id: str) -> list[tuple[Run, Bus]]:
    """
    Filters the given list of RUN, BUS tuples by the given block ID. Any run
    with the same block ID as the given block ID is included in the returned
    list.
    """
    filtered_list: list[tuple[Run, Bus]] = []

    for entry in run_list:
        run = entry[0]

        if block_id == run.block_id:
            filtered_list.append(entry)

    return filtered_list

def _filter_by_bus_tracking_num(run_list: list[tuple[Run, Bus]], tracking_num: str) -> list[tuple[Run, Bus]]:
    """
    Filters the given list of RUN, BUS tuples by the given tracking number. Any
    run whose associated bus's tracking number contains the given tracking
    number as a substring is included in the returned list.
    """
    filtered_list: list[tuple[Run, Bus]] = []

    for entry in run_list:
        bus = entry[1]

        if tracking_num in str(bus.tracking_num):
            filtered_list.append(entry)

    return filtered_list

def _filter_by_bus_model(run_list: list[tuple[Run, Bus]], model: str) -> list[tuple[Run, Bus]]:
    """
    Filters the given list of RUN, BUS tuples by the given model. Any run whose
    associated bus's model contains the given model as a substring is included
    in the returned list.
    """
    filtered_list: list[tuple[Run, Bus]] = []

    for entry in run_list:
        bus = entry[1]

        if model in bus.model:
            filtered_list.append(entry)

    return filtered_list

FILTER_ACTIONS = {
    RunFilterType.DATE: _filter_by_date_range,
    RunFilterType.BLOCK_ID: _filter_by_block_id,
    RunFilterType.BUS_TRACKING_NUM: _filter_by_bus_tracking_num,
    RunFilterType.BUS_MODEL: _filter_by_bus_model
}

