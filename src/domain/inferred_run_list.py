from typing import Iterator
from constants.app_constants import MIN_BUS_TRACKING_NUM, MAX_BUS_TRACKING_NUM
from domain.bus import Bus
from domain.fleet import Fleet
from domain.listener import Listener
from domain.run_assignment import RunAssignment
from domain.validation.exceptions.fleet_error import BusNotFoundError
from utilities.invariant_helper import require_not_none, require_state


class InferredRunList(Listener):
    """
    Represents a list of runs inferred from bus location information. The runs
    are stored as a dictionary mapping bus tracking numbers to their associated
    run assignments.
    """

    def __init__(self, fleet: Fleet):
        require_not_none(fleet, "Fleet should not be None.")

        self._fleet = fleet
        self._runs: dict[int, list[RunAssignment]] = {}

        self._listeners: list[Listener] = []
        self._fleet.register_listener(self)

        self._check_inferred_run_list()

    def _check_inferred_run_list(self) -> None:
        require_not_none(self._fleet, "Fleet should not be None.")

        require_not_none(self._runs, "Run dictionary should not be None.")
        for tracking_num, run_assignments in self._runs.items():
            require_not_none(
                tracking_num,
                "Bus tracking number in run dictionary should not be None."
            )
            require_state(
                MIN_BUS_TRACKING_NUM <= tracking_num <= MAX_BUS_TRACKING_NUM,
                "Bus tracking number should be a 3-digit integer."
            )

            require_not_none(
                run_assignments,
                "Run assignment list in run dictionary should not be None."
            )
            require_state(
                len(run_assignments) > 0,
                "Run assignment list in run dictionary should not be empty."
            )

            for assigned_run in run_assignments:
                require_not_none(assigned_run, "Run assignment in list should not be None.")
                require_state(
                    assigned_run.bus.tracking_num == tracking_num,
                    "Bus in run assignment should have the same tracking number as the key to the "
                    "list of run assignments."
                )

        require_not_none(self._listeners, "Listener list should not be None.")
        for listener in self._listeners:
            require_not_none(listener, "Listener in list should not be None.")

    @property
    def inferred_runs(self) -> list[RunAssignment]:
        """
        :return: a list of run assignments containing all inferred runs,
        sorted by increasing run date (then by increasing bus tracking
        number, then by increasing block ID).
        """
        run_assignments: list[RunAssignment] = []

        for run_assignments in self._runs.values():
            for assigned_run in run_assignments:
                run_assignments.append(assigned_run)

        return sorted(
            run_assignments,
            key=lambda assigned_run: (
                assigned_run.date,
                assigned_run.tracking_num,
                assigned_run.block_id
            )
        )

    @property
    def buses(self) -> list[Bus]:
        """
        :return: the buses in the fleet for this inferred run list.
        """
        return self._fleet.buses

    def __len__(self) -> int:
        """
        :return: the total number of runs in this inferred run list.
        """
        return sum(len(run_list) for run_list in self._runs.values())

    def __iter__(self) -> Iterator[RunAssignment]:
        """
        :return: an iterator over run assignments, sorted by increasing run
        date, then tracking number, then block ID.
        """
        return iter(self.inferred_runs)

    def __getitem__(self, index: int | slice) -> RunAssignment | list[RunAssignment]:
        """
        :param index: the index or the slice to retrieve from this inferred
        run list.
        :return: a RunAssignment (or a list thereof) corresponding to the
        given index or the given slice.
        """
        return self.inferred_runs[index]

    def add_inferred_run(self, run_assignment: RunAssignment) -> None:
        """
        Adds a given run assignment to this inferred run list, or takes no
        action if the given run assignment already exists.
        """
        require_not_none(run_assignment, "Run assignment should not be None.")
        require_state(
            run_assignment.bus is self._fleet.get_bus(run_assignment.tracking_num),
            "The bus in the run assignment should be the same object "
            "as the bus in the fleet."
        )

        tracking_num = run_assignment.tracking_num
        if tracking_num not in self._runs:
            self._runs[tracking_num] = []

        if run_assignment in self._runs[tracking_num]:
            return

        self._runs[tracking_num].append(run_assignment)

        self._check_inferred_run_list()
        self._notify_all()

    def remove_inferred_run(self, run_assignment: RunAssignment,
                            notify: bool=True) -> None:
        """
        Removes a given run assignment from this inferred run list, assuming
        that it exists.
        """
        require_not_none(run_assignment, "Run assignment should not be None.")
        require_state(
            run_assignment in self.inferred_runs,
            "Run assignment to remove should exist in this inferred run list."
        )
        require_state(
            run_assignment.bus is self._fleet.get_bus(run_assignment.tracking_num),
            "The bus in the run assignment should be the same object "
            "as the bus in the fleet."
        )

        self._runs[run_assignment.tracking_num].remove(run_assignment)

        if len(self._runs[run_assignment.tracking_num]) == 0:
            self._runs.pop(run_assignment.tracking_num)

        self._check_inferred_run_list()
        if notify:
            self._notify_all()

    def commit(self, run_assignment: RunAssignment, notify: bool=True) -> bool:
        """
        Adds the run to the corresponding bus in the given run assignment if it
        doesn't already exist, then removes the run assignment from this
        inferred run list.

        :return: True if the run was successfully added to the bus; False
        otherwise (if it already existed).
        """
        require_not_none(run_assignment, "Run assignment should not be None.")
        require_state(
            run_assignment in self.inferred_runs,
            "Run assignment to commit should exist in this inferred run list.")
        require_state(
            run_assignment.bus is self._fleet.get_bus(run_assignment.tracking_num),
            "The bus in the run assignment should be the same object "
            "as the bus in the fleet."
        )

        run, bus = run_assignment.run, run_assignment.bus
        run_already_exists = run in bus.runs

        if not run_already_exists:
            self._fleet.add_run(run_assignment)

        self.remove_inferred_run(run_assignment, notify=False)

        self._check_inferred_run_list()
        if notify:
            self._notify_all()

        return not run_already_exists

    def commit_all(self) -> list[RunAssignment]:
        """
        Adds all run assignments in this inferred run list to the fleet,
        except for those that already exist.

        :return: a list of RunAssignment containing all run assignments added
        to the fleet.
        """
        added_runs: list[RunAssignment] = []

        for assigned_run in self.inferred_runs:
            if self.commit(assigned_run, notify=False):
                added_runs.append(assigned_run)

        self._check_inferred_run_list()
        self._notify_all()

        return added_runs

    def notify(self) -> None:
        """
        Removes any runs associated with buses that are no longer in the fleet.
        """
        changed = False

        for tracking_num in list(self._runs.keys()):
            try:
                self._fleet.get_bus(tracking_num)
                changed = True
            except BusNotFoundError:
                self._runs.pop(tracking_num)

        self._check_inferred_run_list()
        if changed:
            self._notify_all()

    def register_listener(self, l: Listener) -> None:
        require_not_none(l, "Listener should not be None.")

        self._listeners.append(l)

        self._check_inferred_run_list()

    def _notify_all(self) -> None:
        for l in self._listeners:
            l.notify()

