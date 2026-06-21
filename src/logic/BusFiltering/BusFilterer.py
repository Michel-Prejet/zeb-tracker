from typing import Callable
from domain.Bus import Bus
from logic.BusFiltering.BusFilterType import BusFilterType


def build_search_filter_function(filter_text: str, filter_type: BusFilterType,
                                 show_only_active: bool) -> Callable:
    """
    :param filter_text: the string used to filter buses based on whether it
    is contained in the string representation of some attribute.
    :param filter_type: the type of filter to apply to the bus list.
    :param show_only_active: whether to filter out buses with no location info.
    :return: a function that filters a list of buses based on the given
    parameters.
    """
    def filter_function(bus_list: list[Bus]) -> list[Bus]:
        new_list = bus_list.copy()

        if len(filter_text) > 0:
            new_list = FILTER_ACTIONS[filter_type](new_list, filter_text)

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
    return [b for b in bus_list if tracking_num in str(b.tracking_num)]

def _filter_by_year(bus_list: list[Bus], year: str) -> list[Bus]:
    """
    Filters the given list of buses by the given year. Any bus of the same year
    as the given year is included in the returned list.
    """
    return [b for b in bus_list if str(b.year) == str(year)]

def _filter_by_model(bus_list: list[Bus], model: str) -> list[Bus]:
    """
    Filters the given list of buses by the given model. Any bus whose model
    includes the given model as a substring is included in the returned list.
    """
    return [b for b in bus_list if model in b.model]

FILTER_ACTIONS = {
    BusFilterType.TRACKING_NUM: _filter_by_tracking_num,
    BusFilterType.YEAR: _filter_by_year,
    BusFilterType.MODEL: _filter_by_model
}

