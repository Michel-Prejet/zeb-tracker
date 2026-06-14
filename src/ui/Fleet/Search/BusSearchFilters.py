from enum import Enum
from typing import Callable
from domain.Bus import Bus


class SearchFilterType(Enum):
    """
    Represents different filters that can be applied to the fleet during a
    search. Each filter is associated with a lambda function taking as an
    argument a bus list and a string, where the string is used to filter the bus
    list based on whether it is contained in the string representation of the
    selected attribute.
    For example, when TRACKING_NUM is selected with filter "2", all buses
    whose tracking number contains the digit "2" will be displayed.
    """
    TRACKING_NUM = "Tracking number"
    YEAR = "Year"
    MODEL = "Model"

FILTER_ACTIONS = {
    SearchFilterType.TRACKING_NUM: lambda bus_list, search_filter: [b for b in bus_list if search_filter in str(b.tracking_num)],
    SearchFilterType.YEAR: lambda bus_list, search_filter: [b for b in bus_list if search_filter in str(b.year)],
    SearchFilterType.MODEL: lambda bus_list, search_filter: [b for b in bus_list if search_filter in b.model]
}

def build_search_filter_function(filter_text: str, filter_type: SearchFilterType,
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
        new_list = bus_list

        if len(filter_text) > 0:
            new_list = FILTER_ACTIONS[filter_type](new_list, filter_text)

        if show_only_active:
            new_list = [b for b in new_list if b.location_info is not None]

        return new_list

    return filter_function