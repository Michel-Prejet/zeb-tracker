from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from domain.Run import Run
from domain.validation.exceptions.BusError import DuplicateRunError
from utilities.InvariantHelper import require_not_none, require_state


class InferredRunList:
    """
    Represents a list of runs inferred from bus location information. The runs
    are stored as a dictionary mapping bus tracking numbers to their associated
    runs. Also stores a fleet to which the inferred runs can eventually be added.
    """

    def __init__(self, fleet: Fleet):
        self.fleet = fleet
        self.runs: dict[int, Run] = {}
        self.listeners: list[Listener] = []

        self._check_inferred_run_list()

    def __iter__(self):
        return iter(self.runs.keys())

    def __getitem__(self, index: int | slice):
        return list(self.runs.keys())[index]

    def __len__(self):
        return len(self.runs)

    def _check_inferred_run_list(self) -> None:
        require_not_none(self.fleet, "Fleet should not be None.")
        require_not_none(self.runs, "Run dictionary should not be None.")
        for key in self.runs.keys():
            require_not_none(key, "Key in run dictionary should not be None.")
            require_state(Bus.MIN_TRACKING_NUM <= key <= Bus.MAX_TRACKING_NUM,
                          "Key should contain exactly 3 digits.")
            require_not_none(self.runs[key],
                             "Run in run dictionary should not be None.")

    def get(self, bus_tracking_num: int) -> Run:
        """
        :param bus_tracking_num: the bus tracking number for which to retrieve
        the associated run in this dictionary.
        :return: the run associated with the given bus tracking number.
        """
        require_state(bus_tracking_num in self.runs,
                      "Bus tracking number should exist in the run dictionary.")
        return self.runs[bus_tracking_num]

    def add(self, bus_tracking_num: int, run: Run) -> None:
        """
        Adds a given run to this run dictionary associated with a given bus
        tracking number. Assumes that the tracking number corresponds to a bus
        in the fleet and has not already been assigned a run in this list. The
        run is not added if it already exists for the given bus in the fleet.

        :param bus_tracking_num: the tracking number of the bus for which to
        infer a run.
        :param run: the run to add to this run dictionary under the given
        bus tracking number.
        """
        require_not_none(bus_tracking_num,
                         "Bus tracking number should not be None.")
        require_state(Bus.MIN_TRACKING_NUM <= bus_tracking_num <= Bus.MAX_TRACKING_NUM,
                      "Bus tracking number should contain exactly 3 digits.")
        require_state(bus_tracking_num in self.fleet.buses,
                      "Bus tracking number should correspond to a bus in the fleet.")
        require_state(bus_tracking_num not in self.runs,
                      "Each bus can only be associated with one run.")
        require_not_none(run, "Run should not be None.")

        if not self._check_if_run_already_exists(bus_tracking_num, run):
            self.runs[bus_tracking_num] = run
            self._notify_all()

    def remove(self, bus_tracking_num: int, notify: bool=True) -> None:
        """
        Removes the entry in this dictionary associated with the given bus
        tracking number. Assumes that an entry exists for the given tracking
        number.

        :param bus_tracking_num: the tracking number associated with the
        key/value pair to remove.
        :param notify: whether to notify listeners of changes.
        """
        require_not_none(bus_tracking_num,
                         "Bus tracking number should not be None.")
        require_state(bus_tracking_num in self.runs,
                      "Key to remove should exist in the run dictionary.")

        self.runs.pop(bus_tracking_num)

        if notify:
            self._notify_all()

    def add_to_fleet(self, bus_tracking_num: int, notify: bool=True) -> tuple[Run, Bus] | None:
        """
        Adds the run associated with the given tracking number to the
        corresponding bus in the fleet, then removes the key/value pair from
        this run dictionary. Assumes that the given tracking number exists as
        a key in this run dictionary and corresponds to a bus in the fleet.

        :param bus_tracking_num: the tracking number of a bus to which to add
        the inferred run.
        :param notify: whether to notify listeners of changes.
        :return: a tuple of the form (RUN, BUS), where RUN is the run that was
        added to BUS; or None if the run was not successfully added.
        """
        require_not_none(bus_tracking_num,
                         "Bus tracking number should not be None.")
        require_state(bus_tracking_num in self.runs,
                      "Bus tracking number should exist as a key in the run dictionary.")
        require_state(bus_tracking_num in self.fleet.buses,
                      "Bus tracking number should correspond to a bus in the fleet.")

        bus = self.fleet.get_bus(bus_tracking_num)
        run = self.runs[bus_tracking_num]

        try:
            bus.add_run(run)
        except DuplicateRunError:
            return None

        self.remove(bus_tracking_num, False)

        if notify:
            self._notify_all()
        return run, bus

    def add_all_to_fleet(self) -> list[tuple[Run, Bus]]:
        """
        Adds all runs in the dictionary to their associated buses in the fleet.

        :return: a list of tuples of the form (RUN, BUS) where RUN is the run
        that was successfully added to BUS.
        """
        added_runs: list[tuple[Run, Bus]] = []
        runs_copy = self.runs.copy()

        for tracking_num in runs_copy.keys():
            added_run = self.add_to_fleet(tracking_num, False)

            if added_run is not None:
                added_runs.append(added_run)

        self._notify_all()
        return added_runs

    def register_listener(self, l: Listener) -> None:
        self.listeners.append(l)

    def _notify_all(self) -> None:
        for l in self.listeners:
            l.notify()

    def _check_if_run_already_exists(self, bus_tracking_num: int, run: Run) -> bool:
        bus = self.fleet.get_bus(bus_tracking_num)
        require_not_none(bus,
                         "Bus tracking number should correspond to a bus in the fleet.")

        return bus.contains(run)

