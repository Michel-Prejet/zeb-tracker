from datetime import date
from utilities.InvariantHelper import require_not_none, require_state


class Run:
    """
    Represents a ZEB bus run consisting of one or more routes, a date,
    and a block ID (e.g. 1-52). A run is a sequence of back-to-back
    trips performed by a single vehicle.
    """

    def __init__(self, block_id: str, run_date: date):
        self.block_id = block_id
        self.run_date = run_date

        self._check_run()

    def _check_run(self) -> None:
        require_not_none(self.block_id, "Block ID should not be None.")
        require_state(len(self.block_id.strip()) >= 1, "Block ID should not be empty.")
        require_not_none(self.run_date, "Date should not be None.")

    def __eq__(self, other) -> bool:
        return isinstance(other, Run) and self.run_date == other.run_date and self.block_id == other.block_id

    def __lt__(self, other) -> bool:
        return self.run_date <= other.run_date