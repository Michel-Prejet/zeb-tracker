from typing import Callable
from domain.bus import Bus
from logic.bus_filtering.bus_filter_type import BusFilterType
from utilities.invariant_helper import require_not_none


def build_search_filter_function(filter_input: str, filter_type: BusFilterType,
                                 show_only_active: bool) -> Callable:
    """
    Creates a function that filters a list of buses based on the given filter
    type and input, as well as whether to include buses without location
    info.
    """
    require_not_none(filter_input, "Filter input should not be None.")
    require_not_none(filter_type, "Filter type should not be None.")
    require_not_none(show_only_active, "'Show only active' flag should not be None.")

    def filter_function(bus_list: list[Bus]) -> list[Bus]:
        _require_valid_bus_list(bus_list)

        new_list = bus_list.copy()

        if filter_input:
            new_list = FILTER_ACTIONS[filter_type](new_list, filter_input)

        if show_only_active:
            new_list = [b for b in new_list if b.location_info is not None]

        return new_list

    return filter_function

def _filter_by_tracking_num(bus_list: list[Bus], tracking_num: str) -> list[Bus]:
    """
    Filters the given list of buses by the given tracking number. Any bus whose
    tracking number includes the given tracking number as a substring is included
    in the returned list.
    """
    _require_valid_bus_list(bus_list)
    require_not_none(tracking_num, "Tracking number should not be None.")

    return [b for b in bus_list if tracking_num in str(b.tracking_num)]

def _filter_by_year(bus_list: list[Bus], year: str) -> list[Bus]:
    """
    Filters the given list of buses by the given year. Any bus of the same year
    as the given year is included in the returned list.
    """
    _require_valid_bus_list(bus_list)
    require_not_none(year, "Year should not be None.")

    return [b for b in bus_list if str(b.year) == str(year)]

def _filter_by_model(bus_list: list[Bus], model: str) -> list[Bus]:
    """
    Filters the given list of buses by the given model. Any bus whose model
    includes the given model as a substring is included in the returned list.
    """
    _require_valid_bus_list(bus_list)
    require_not_none(model, "Model should not be None.")

    return [b for b in bus_list if model in b.model]

def _require_valid_bus_list(bus_list: list[Bus]) -> None:
    require_not_none(bus_list, "Bus list should not be None.")
    for bus in bus_list:
        require_not_none(bus, "Bus in list should not be None.")

FILTER_ACTIONS = {
    BusFilterType.TRACKING_NUM: _filter_by_tracking_num,
    BusFilterType.YEAR: _filter_by_year,
    BusFilterType.MODEL: _filter_by_model
}

