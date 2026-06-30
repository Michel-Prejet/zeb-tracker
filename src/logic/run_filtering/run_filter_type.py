from enum import Enum


class RunFilterType(Enum):
    """
    Represents different filters that can be applied to the list of runs during
    a search.
    """
    DATE = "Date"
    BLOCK_ID = "Block ID"
    BUS_TRACKING_NUM = "Bus"
    BUS_MODEL = "Model"