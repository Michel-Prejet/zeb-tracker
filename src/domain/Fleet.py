from domain.Bus import Bus
from domain.Listener import Listener
from domain.validation.exceptions.FleetError import BusNotFoundError, DuplicateBusError
from utilities.InvariantHelper import require_not_none, require_state


class Fleet:
    """
    Represents a ZEB fleet consisting of buses with unique tracking numbers.
    """

    def __init__(self):
        self.buses: dict[int, Bus] = {}
        self.listeners: list[Listener] = []

        self._check_fleet()

    def _check_fleet(self) -> None:
        require_not_none(self.buses, "Bus list should not be None.")
        for key in self.buses.keys():
            require_state(Bus.MIN_TRACKING_NUM <= key <= Bus.MAX_TRACKING_NUM,
                          "Key should contain exactly 3 digits.")
        for bus in self.buses.values():
            require_not_none(bus, "Bus in bus list should not be None.")

    def sorted_buses(self) -> list[Bus]:
        """
        :return: a list containing all buses in this fleet, sorted by tracking
        number in increasing order.
        """
        return sorted(self.buses.values())

    def num_runs(self) -> int:
        """
        :return: the total number of runs completed by all buses in this fleet.
        """
        total_runs = 0

        for bus in self.buses.values():
            total_runs += bus.num_runs()

        return total_runs

    def percent_of_runs(self, bus: Bus) -> float:
        """
        :param bus: the bus for which to calculate the percentage of runs
        completed in this fleet.
        :return: a float representing the percentage of runs completed by
        the given bus in this fleet.
        """
        if self.num_runs() == 0:
            return 0
        return round(bus.num_runs() / self.num_runs(), 2)


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
        self._notify_all()

    def remove_bus(self, bus: Bus) -> None:
        """
        Removes a given bus from this fleet. Assumes that the bus exists
        in the fleet.

        :param bus: the bus to remove from this fleet.
        """
        require_state(bus in self.buses.values(), "Bus to remove should be in fleet.")

        self.buses.pop(bus.tracking_num)
        self._notify_all()

    def _notify_all(self) -> None:
        for listener in self.listeners:
            listener.notify()

    def register_listener(self, l: Listener) -> None:
        require_not_none(l, "Listener should not be None.")
        self.listeners.append(l)