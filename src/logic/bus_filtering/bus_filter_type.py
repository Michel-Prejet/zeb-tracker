from enum import Enum


class BusFilterType(Enum):
    """
    Represents different filters that can be applied to the fleet during a
    search.
    """
    TRACKING_NUM = "Tracking number"
    YEAR = "Year"
    MODEL = "Model"