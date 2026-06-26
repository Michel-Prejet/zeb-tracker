from constants.app_constants import MIN_BUS_TRACKING_NUM, MAX_BUS_TRACKING_NUM
from domain.bus import Bus
from domain.listener import Listener
from domain.location_info.LocationInfo import LocationInfo
from domain.run_assignment import RunAssignment
from domain.validation.exceptions.FleetError import BusNotFoundError, DuplicateBusError
from utilities.InvariantHelper import require_not_none, require_state
from datetime import date


class Fleet:
    """
    Represents a ZEB fleet consisting of buses with unique tracking numbers.
    Coordinates changes to buses and their completed runs.
    """

    def __init__(self):
        self._buses: dict[int, Bus] = {}
        self._listeners: list[Listener] = []

        self._check_fleet()

    def _check_fleet(self) -> None:
        require_not_none(self._buses, "Bus dictionary should not be None.")

        for tracking_num, bus in self._buses.items():
            require_not_none(
                tracking_num,
                "Tracking number in bus dictionary should not be None."
            )
            require_state(
                MIN_BUS_TRACKING_NUM <= tracking_num <= MAX_BUS_TRACKING_NUM,
                "Tracking number should be a three-digit integer."
            )

            require_not_none(
                bus,
                "Bus in dictionary should not be None."
            )
            require_state(
                tracking_num == bus.tracking_num,
                "Key should correspond to the bus's tracking number."
            )

        require_not_none(self._listeners, "Listener list should not be None.")
        for listener in self._listeners:
            require_not_none(listener, "Listener in list should not be None.")

    @property
    def buses(self) -> list[Bus]:
        """
        :return: a list containing all buses in this fleet, sorted by
        increasing tracking number.
        """
        return sorted(self._buses.values())

    @property
    def runs(self) -> list[RunAssignment]:
        """
        :return: a list of RunAssignment containing all runs completed by this
        fleet along with their corresponding buses, sorted by decreasing run
        date.
        """
        runs: list[RunAssignment] = []

        for bus in self._buses.values():
            for run in bus.runs:
                runs.append(RunAssignment(run=run, bus=bus))

        return sorted(
            runs,
            key=lambda r: r.date, reverse=True
        )

    def num_runs(self) -> int:
        """
        :return: the total number of runs completed by all buses in this fleet.
        """
        return sum(bus.num_runs() for bus in self._buses.values())

    def get_bus(self, tracking_num: int) -> Bus:
        """
        Searches for a bus in this fleet with a given 3-digit tracking number.
        Raises an exception if no such bus was found.
        """
        require_not_none(tracking_num, "Tracking number should not be None.")
        require_state(
            MIN_BUS_TRACKING_NUM <= tracking_num <= MAX_BUS_TRACKING_NUM,
            "Tracking number should be a three-digit integer."
        )

        bus = self._buses.get(tracking_num)

        if bus is None:
            raise BusNotFoundError()

        return bus

    def get_runs_starting_from(self, run_date: date) -> list[RunAssignment]:
        """
        :return: a list of RunAssignment containing all runs completed by this
        fleet along with their corresponding buses starting at a given date,
        sorted by decreasing run date.
        """
        require_not_none(run_date, "Run date should not be None.")

        return [r for r in self.runs if r.date >= run_date]

    def add_bus(self, bus: Bus) -> None:
        """
        Adds a given bus to this fleet. Raises an exception if a bus already
        exists with the same tracking number.
        """
        require_not_none(bus, "Bus should not be None.")

        if bus.tracking_num in self._buses:
            raise DuplicateBusError()

        self._buses[bus.tracking_num] = bus

        require_state(bus.tracking_num in self._buses,
                      "Bus should have been added.")
        self._check_fleet()
        self._notify_all()

    def remove_bus(self, bus: Bus) -> None:
        """
        Removes a given bus from this fleet, assuming that it already
        exists.
        """
        require_not_none(bus, "Bus should not be None.")
        require_state(
            bus.tracking_num in self._buses,
            "Bus to remove should be in fleet."
        )
        require_state(
            bus is self.get_bus(bus.tracking_num),
            "Bus should come from this fleet."
        )

        self._buses.pop(bus.tracking_num)

        require_state(
            bus.tracking_num not in self._buses,
            "Bus should have been removed."
        )
        self._check_fleet()
        self._notify_all()

    def add_run(self, run_assignment: RunAssignment) -> None:
        """
        Adds the run to the bus in the given run assignment, assuming that the
        bus exists in this fleet.
        """
        require_not_none(run_assignment, "Run assignment should not be None.")
        require_state(run_assignment.tracking_num in self._buses,
                      "Bus should exist in this fleet.")

        run = run_assignment.run
        bus = self.get_bus(run_assignment.tracking_num)
        require_state(
            run_assignment.bus is bus,
            "The bus in the RunAssignment should be the same object "
                    "as the bus in this fleet."
        )

        bus.add_run(run)

        self._check_fleet()
        self._notify_all()

    def remove_run(self, run_assignment: RunAssignment) -> None:
        """
        Removes the run from the bus in the given run assignment, assuming that
        the bus exists in this fleet and the run exists for that bus.
        """
        require_not_none(run_assignment, "Run assignment should not be None.")
        require_state(run_assignment.tracking_num in self._buses,
                      "Bus should exist in this fleet.")

        run = run_assignment.run
        bus = self.get_bus(run_assignment.tracking_num)
        require_state(
            run_assignment.bus is bus,
            "The bus in the RunAssignment should be the same object "
            "as the bus in this fleet."
        )

        bus.remove_run(run)

        self._check_fleet()
        self._notify_all()

    def set_bus_location_info(self, bus_tracking_num: int, location_info: LocationInfo) -> None:
        """
        Assigns the given location info to the bus in this fleet with the
        given tracking number.
        """
        require_not_none(
            bus_tracking_num,
            "Bus tracking number should not be None."
        )
        require_state(
            MIN_BUS_TRACKING_NUM <= bus_tracking_num <= MAX_BUS_TRACKING_NUM,
            "Bus tracking number should be a 3-digit integer."
        )
        require_state(
            bus_tracking_num in self._buses,
            "Bus should exist in this fleet."
        )
        require_not_none(location_info,"Location info should not be None.")

        bus = self.get_bus(bus_tracking_num)
        bus.set_location_info(location_info)

        self._check_fleet()
        self._notify_all()

    def reset_bus_location_info(self, bus_tracking_num: int) -> None:
        """
        Clears the location info for the bus in this fleet with the given
        tracking number.
        """
        require_not_none(
            bus_tracking_num,
            "Bus tracking number should not be None."
        )
        require_state(
            MIN_BUS_TRACKING_NUM <= bus_tracking_num <= MAX_BUS_TRACKING_NUM,
            "Bus tracking number should be a 3-digit integer."
        )
        require_state(
            bus_tracking_num in self._buses,
            "Bus should exist in this fleet."
        )

        bus = self.get_bus(bus_tracking_num)
        bus.reset_location_info()

        self._check_fleet()
        self._notify_all()

    def register_listener(self, l: Listener) -> None:
        require_not_none(l, "Listener should not be None.")

        self._listeners.append(l)

        self._check_fleet()

    def _notify_all(self) -> None:
        for listener in self._listeners:
            listener.notify()