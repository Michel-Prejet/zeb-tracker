from constants.app_constants import MIN_BUS_YEAR, MIN_BUS_TRACKING_NUM, MAX_BUS_TRACKING_NUM
from domain.listener import Listener
from domain.run import Run
from domain.location_info.location_info import LocationInfo
from domain.validation.exceptions.bus_error import DuplicateRunError
from utilities.invariant_helper import require_not_none, require_state
import bisect


class Bus:
    """
    Represents a bus in the ZEB fleet with a 3-digit tracking number, a year,
    a model, and a list of completed runs.
    """
    def __init__(self, tracking_num: int, year: int, model: str):
        require_not_none(tracking_num,
                         "Bus tracking number should not be None.")
        require_not_none(year,
                         "Bus year should not be None.")
        require_not_none(model,
                         "Bus model should not be None.")

        self._tracking_num = tracking_num
        self._year = year
        self._model = model.strip()
        self._runs: list[Run] = []
        self._location_info: LocationInfo | None = None

        self._listeners: list[Listener] = []

        self._check_bus()

    def _check_bus(self) -> None:
        require_not_none(
            self._tracking_num,
            "Tracking number should not be None."
        )
        require_state(
            MIN_BUS_TRACKING_NUM <= self._tracking_num <= MAX_BUS_TRACKING_NUM,
            f"Tracking number should be a three-digit integer."
        )

        require_not_none(
            self._year,
            "Year should not be None."
        )
        require_state(
            self._year >= MIN_BUS_YEAR,
            f"Year should be greater than or equal to {MIN_BUS_YEAR}."
        )

        require_not_none(self._model, "Model should not be None.")
        require_state(
            len(self._model) >= 1,
            "Model should not be empty or only whitespace."
        )

        require_not_none(self._runs, "Run list should not be None.")
        for run in self._runs:
            require_not_none(run, "Run in list should not be None.")

        require_not_none(self._listeners,
                         "Listener list should not be None.")
        for listener in self._listeners:
            require_not_none(listener, "Listener in list should not be None.")

    @property
    def tracking_num(self) -> int:
        return self._tracking_num

    @property
    def year(self) -> int:
        return self._year

    @property
    def model(self) -> str:
        return self._model

    @property
    def runs(self) -> list[Run]:
        """
        :return: a shallow copy of this bus's run list.
        """
        return list(self._runs)

    @property
    def location_info(self) -> LocationInfo | None:
        return self._location_info

    def __eq__(self, other) -> bool:
        """
        Determines whether a given object is equal to this bus. A bus is equal
        to another bus if they have the same tracking number.
        """
        return (
            isinstance(other, Bus)
            and self.tracking_num == other.tracking_num
        )

    def __lt__(self, other) -> bool:
        """
        Determines whether this bus is less than a given object. The comparison
        is based only on the bus tracking numbers.
        """
        if not isinstance(other, Bus):
            return NotImplemented

        return self.tracking_num < other.tracking_num

    def num_runs(self) -> int:
        return len(self._runs)

    def first_run(self) -> Run | None:
        """
        :return: the run with the earliest date for this bus, or None if there
        are no runs.
        """
        return self._runs[0] if self._runs else None

    def last_run(self) -> Run | None:
        """
        :return: the run with the latest date for this bus, or None if there
        are no runs.
        """
        return self._runs[-1] if self._runs else None

    def contains(self, run: Run) -> bool:
        """
        :return: True if the given run exists in the bus's list of runs; False
        otherwise.
        """
        require_not_none(run, "Run should not be None.")

        return run in self._runs

    def set_location_info(self, info: LocationInfo) -> None:
        require_not_none(info, "Location info should not be None.")

        self._location_info = info

        self._check_bus()
        self._notify_all()

    def reset_location_info(self) -> None:
        self._location_info = None

        self._check_bus()
        self._notify_all()

    def add_run(self, run: Run) -> None:
        """
        Adds a new run to this bus. Maintains the run list in sorted order by
        increasing run date. Raises a DuplicateRunError if the run was already
        added to this bus.
        """
        require_not_none(run, "Run should not be None.")

        if run in self._runs:
            raise DuplicateRunError()

        bisect.insort(self._runs, run)

        require_state(run in self._runs,
                      "Run should have been added to this bus.")
        self._check_bus()
        self._notify_all()

    def remove_run(self, run: Run) -> None:
        """
        Removes a given run from this bus. Assumes that the given run exists
        in this bus's run list.
        """
        require_not_none(run, "Run should not be None.")
        require_state(run in self._runs,
                      "Run to remove should exist in this bus's list of runs.")

        self._runs.remove(run)

        require_state(run not in self._runs,
                      "Run should have been removed from this bus.")
        self._check_bus()
        self._notify_all()

    def register_listener(self, l: Listener) -> None:
        require_not_none(l, "Listener should not be None.")

        self._listeners.append(l)

        self._check_bus()

    def _notify_all(self) -> None:
        for listener in self._listeners:
            listener.notify()

