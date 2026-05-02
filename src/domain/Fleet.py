from domain.Bus import Bus
from domain.validation.exceptions.FleetError import BusNotFoundError, DuplicateBusError
from utilities.InvariantHelper import require_not_none, require_state


class Fleet:
    """
    Represents a ZEB fleet consisting of buses with unique tracking numbers.
    """

    def __init__(self):
        self.buses: dict[int, Bus] = {}

        self._check_fleet()

    def _check_fleet(self) -> None:
        require_not_none(self.buses, "Bus list should not be None.")
        for key in self.buses.keys():
            require_state(Bus.MIN_TRACKING_NUM <= key <= Bus.MAX_TRACKING_NUM,
                          "Key should contain exactly 3 digits.")
        for bus in self.buses.values():
            require_not_none(bus, "Bus in bus list should not be None.")

    def get_bus(self, tracking_num: int) -> Bus:
        """
        Searches for a bus in this fleet with a given 3-digit tracking number.
        Raises an exception if no such bus was found.

        :param tracking_num: the 3-digit tracking number of the bus to retrieve.
        :return: the bus in this fleet with the given tracking number.
        """
        require_not_none(tracking_num, "Tracking number should not be None.")
        require_state(Bus.MIN_TRACKING_NUM <= tracking_num <= Bus.MAX_TRACKING_NUM,
                      "Tracking number should contain exactly 3 digits.")

        result = self.buses.get(tracking_num)

        if result is None:
            raise BusNotFoundError()
        else:
            return result

    def add_bus(self, bus: Bus) -> None:
        """
        Adds a given bus to this fleet. Raises an exception if a bus already
        exists with the same tracking number.

        :param bus: the bus to add to this fleet.
        """
        require_not_none(bus, "Bus should not be None.")

        if bus.tracking_num in self.buses.keys():
            raise DuplicateBusError()

        self.buses[bus.tracking_num] = bus