class FleetError(Exception):
    """
    Exception raised whenever an error occurs relating to a fleet object.
    """
    pass

class BusNotFoundError(FleetError):
    pass

class DuplicateBusError(FleetError):
    pass