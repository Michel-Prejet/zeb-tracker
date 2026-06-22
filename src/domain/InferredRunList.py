from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from domain.Run import Run
from domain.validation.exceptions.BusError import DuplicateRunError
from domain.validation.exceptions.FleetError import BusNotFoundError
from utilities.InvariantHelper import require_not_none, require_state


class InferredRunList(Listener):
    """
    Represents a list of runs inferred from bus location information. The runs
    are stored as a dictionary mapping bus tracking numbers to their associated
    runs. Also stores a fleet to which the inferred runs can eventually be added.
    """

    def __init__(self, fleet: Fleet):
        self.fleet = fleet
        self.runs: dict[int, set[Run]] = {}
        self.listeners: list[Listener] = []
        self.size = 0

        self.fleet.register_listener(self)

        self._check_inferred_run_list()

    def __iter__(self):
        """
        :return: a list of RUN, BUS tuples containing every run in this
        inferred run list along with its corresponding bus.
        """
        return iter(self._build_iterable_list())

    def __getitem__(self, index: int | slice):
        """
        :param index: the index or the slice to retrieve from this inferred
        run list.
        :return: a RUN, BUS tuple (or a list thereof) corresponding to the given
        index or the given slice.
        """
        return self._build_iterable_list()[index]

    def __len__(self):
        """
        :return: the total number of runs in this inferred run list.
        """
        return self.size

    def _check_inferred_run_list(self) -> None:
        require_not_none(self.fleet, "Fleet should not be None.")
        require_not_none(self.runs, "Run dictionary should not be None.")
        for key in self.runs.keys():
            require_not_none(key, "Key in run dictionary should not be None.")
            require_state(Bus.MIN_TRACKING_NUM <= key <= Bus.MAX_TRACKING_NUM,
                          "Key should contain exactly 3 digits.")
            require_not_none(self.runs[key],
                             "Run list in run dictionary should not be None.")
            require_state(len(self.runs[key]) > 0,
                          "Run list in run dictionary should not be empty.")
            for run in self.runs[key]:
                require_not_none(run, "Run in run list in run dictionary should not be None.")
        require_not_none(self.size, "Size should not be None.")
        require_state(self.size >= 0, "Size should not be negative.")

    def get(self, bus_tracking_num: int) -> set[Run]:
        """
        :param bus_tracking_num: the bus tracking number for which to retrieve
        the associated run in this dictionary.
        :return: the set of runs associated with the given bus tracking number.
        """
        require_state(bus_tracking_num in self.runs,
                      "Bus tracking number should exist in the run dictionary.")
        return self.runs[bus_tracking_num].copy()

    def add(self, bus_tracking_num: int, run: Run) -> None:
        """
        Adds a given run to this run dictionary associated with a given bus
        tracking number. Assumes that the tracking number corresponds to a bus
        in the fleet.

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
        require_not_none(run, "Run should not be None.")

        if not self._check_if_run_already_exists(bus_tracking_num, run):
            if bus_tracking_num not in self.runs:
                self.runs[bus_tracking_num] = set()

            if run in self.runs[bus_tracking_num]:
                return

            self.runs[bus_tracking_num].add(run)
            self.size += 1

            self._notify_all()

        self._check_inferred_run_list()

    def remove(self, run: Run, bus: Bus, notify: bool=True) -> None:
        """
        Removes the given run stored under the given bus's tracking number.
        Assumes that the run exists for the given bus in this dictionary.

        :param run: the run to remove from the dictionary.
        :param bus: the bus under which the given run is found.
        :param notify: whether to notify listeners of changes.
        """
        require_not_none(run, "Run should not be None.")
        require_not_none(bus, "Bus should not be None.")
        require_state(bus.tracking_num in self.runs,
                      "The bus tracking number for the run to remove "
                      "should exist in the run dictionary.")
        require_state(run in self.runs[bus.tracking_num],
                      "The run to remove should exist in the run dictionary.")

        self.runs[bus.tracking_num].remove(run)

        if len(self.runs[bus.tracking_num]) == 0:
            self.runs.pop(bus.tracking_num)

        self.size -= 1

        if notify:
            self._notify_all()

        self._check_inferred_run_list()

    def add_to_fleet(self, run: Run, bus: Bus, notify: bool=True) -> bool:
        """
        Adds the given run to the given bus and removes it from this inferred
        run list. Assumes that the given run exists for the given bus in this
        dictionary.

        :param run: the run to add to the fleet from this inferred run list.
        :param bus: the bus to which to add the given run.
        :param notify: whether to notify listeners of changes.
        :return: True if the run was successfully added, False otherwise.
        """
        require_not_none(run, "Run should not be None.")
        require_not_none(bus, "Bus should not be None.")
        require_state(bus.tracking_num in self.runs,
                      "The bus tracking number for the run to add to the fleet "
                      "should exist in the run dictionary.")
        require_state(run in self.runs[bus.tracking_num],
                      "The run to add to the fleet should exist in the run dictionary.")

        try:
            bus.add_run(run)
        except DuplicateRunError:
            return False

        self.remove(run, bus, False)

        self._check_inferred_run_list()
        if notify:
            self._notify_all()
        return True

    def add_all_to_fleet(self) -> list[tuple[Run, Bus]]:
        """
        Adds all runs in the dictionary to their associated buses in the fleet.

        :return: a list of tuples of the form (RUN, BUS) where RUN is the run
        that was successfully added to BUS.
        """
        added_runs: list[tuple[Run, Bus]] = []

        for tracking_num, runs in list(self.runs.items()):
            bus = self.fleet.get_bus(tracking_num)

            for run in list(runs):
                success = self.add_to_fleet(run, bus, notify=False)

                if success:
                    added_runs.append((run, bus))

        self._check_inferred_run_list()
        self._notify_all()
        return added_runs

    def notify(self) -> None:
        """
        Removes any runs associated with buses that are no longer in the fleet.
        """
        for tracking_num in list(self.runs.keys()):
            try:
                self.fleet.get_bus(tracking_num)
            except BusNotFoundError:
                num_removed = len(self.runs[tracking_num])
                self.runs.pop(tracking_num)
                self.size -= num_removed

        self._check_inferred_run_list()
        self._notify_all()

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

    def _build_iterable_list(self) -> list[tuple[Run, Bus]]:
        iterable_list: list[tuple[Run, Bus]] = []

        for tracking_num in self.runs.keys():
            bus = self.fleet.get_bus(tracking_num)

            for run in self.runs[tracking_num]:
                iterable_list.append((run, bus))

        return sorted(
            iterable_list,
            key=lambda pair: (
                pair[0].run_date,
                pair[1].tracking_num,
                pair[0].block_id
            )
        )

