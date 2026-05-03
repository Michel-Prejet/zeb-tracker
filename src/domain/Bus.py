from domain.Run import Run
from domain.validation.exceptions.BusError import DuplicateRunError
from utilities.InvariantHelper import require_not_none, require_state
import bisect


class Bus:
    """
    Represents a bus in the ZEB fleet with a 3-digit tracking number, a year
    and model, and a list of completed runs.
    """

    MIN_TRACKING_NUM = 100
    MAX_TRACKING_NUM = 999
    MIN_YEAR = 2000
    UNKNOWN_DATE_PLACEHOLDER = "never"

    def __init__(self, tracking_num: int, year: int, model: str):
        self.tracking_num = tracking_num
        self.year = year
        self.model = model
        self.runs: list[Run] = []

        self._check_bus()

    def _check_bus(self) -> None:
        require_not_none(self.tracking_num,
                         "Tracking number should not be None.")
        require_state(Bus.MIN_TRACKING_NUM <= self.tracking_num <= Bus.MAX_TRACKING_NUM,
                      "Tracking number must have exactly three digits.")
        require_not_none(self.year, "Year should not be None.")
        require_state(self.year >= Bus.MIN_YEAR,
                      "Year should be greater than or equal to 2000.")
        require_not_none(self.model, "Model should not be None.")
        require_state(len(self.model.strip()) >= 1, "Model should not be empty.")
        require_not_none(self.runs, "Run list should not be None.")
        for run in self.runs:
            require_not_none(run, "Run in run list should not be None.")

    def add_run(self, run: Run) -> None:
        """
        Adds a new run to the list of runs for this bus, maintaining sorted
        order so that the list is ordered by increasing start dates. Raises
        an exception if the run already exists for this bus.

        :param run: the run completed by this bus.
        """
        require_not_none(run, "Run should not be None.")

        if run in self.runs:
            raise DuplicateRunError()

        bisect.insort(self.runs, run)

        self._check_bus()

    def num_runs(self) -> int:
        return len(self.runs)

    def first_run(self) -> Run | None:
        """
        :return: the first run completed by this bus.
        """
        if len(self.runs) == 0:
            return None
        return self.runs[0]

    def last_run(self) -> Run | None:
        """
        :return: the last run completed by this bus.
        """
        if len(self.runs) == 0:
            return None
        return self.runs[len(self.runs) - 1]

    def last_run_as_str(self) -> str:
        """
        :return: the last run completed by this bus as a string of the form
        MONTH DAY, YEAR (e.g. May 2, 2026) or "Never" if this bus hasn't
        completed any runs.
        """
        if self.last_run() is None:
            return Bus.UNKNOWN_DATE_PLACEHOLDER
        return self.last_run().run_date.strftime("%B %-d, %Y")

    def __lt__(self, other) -> bool:
        return self.tracking_num < other.tracking_num

