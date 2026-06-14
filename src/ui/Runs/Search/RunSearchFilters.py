from enum import Enum


class SearchFilterType(Enum):
    """
    Represents different filters that can be applied to the list of runs during
    a search. Each filter is associated with a lambda function taking as an
    argument a list of (Run, Bus) tuples and a string, where the string is used
    to filter the run list based on whether it is contained in the string
    representation of the selected attribute (except for block IDs, which
    require an exact match).
    For example, when DATE is selected with filter "2026-05", all runs in
    May 2026 will be displayed.
    """
    DATE = "Date"
    BLOCK_ID = "Block ID"
    BUS_TRACKING_NUM = "Bus"
    BUS_MODEL = "Model"

FILTER_ACTIONS = {
    SearchFilterType.DATE: lambda run_list, start_date, end_date: [r for r in run_list if start_date <= r[0].run_date <= end_date],
    SearchFilterType.BLOCK_ID: lambda run_list, search_filter: [r for r in run_list if search_filter == r[0].block_id],
    SearchFilterType.BUS_TRACKING_NUM: lambda run_list, search_filter: [r for r in run_list if search_filter in str(r[1].tracking_num)],
    SearchFilterType.BUS_MODEL: lambda run_list, search_filter: [r for r in run_list if search_filter in r[1].model]
}