from domain.Run import Run
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
        order so that the list is ordered by increasing start dates/times.

        :param run: the run completed by this bus.
        """
        require_not_none(run, "Run should not be None.")

        bisect.insort(self.runs, run)

        self._check_bus()

    def num_runs(self) -> int:
        return len(self.runs)

    def routes(self) -> set[str]:
        """
        :return: a set of strings containing all routes served by this bus.
        """
        routes = set()
        for run in self.runs:
            for route in run.routes:
                routes.add(route)
        return routes

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

