from datetime import date
from utilities.InvariantHelper import require_not_none, require_state


class Run:
    """
    Represents a ZEB bus run consisting of a date and a block ID (e.g. 1-52).
    A run is a sequence of back-to-back trips performed by a single vehicle.
    """

    def __init__(self, block_id: str, run_date: date):
        require_not_none(block_id, "Block ID should not be None.")
        require_not_none(run_date, "Run date should not be None.")

        self._block_id = block_id.strip()
        self._run_date = run_date
        self.id: int | None = None

        self._check_run()

    def _check_run(self) -> None:
        require_not_none(self.block_id, "Block ID should not be None.")
        require_state(len(self.block_id) >= 1,
                      "Block ID should not be empty or only whitespace.")
        require_not_none(self.run_date, "Date should not be None.")

    @property
    def block_id(self) -> str:
        return self._block_id

    @property
    def run_date(self) -> date:
        return self._run_date

    def __eq__(self, other) -> bool:
        """
        Determines whether a given object is equal to this run. A run is
        equal to another run if both have the same date and block ID.
        """
        return (
            isinstance(other, Run)
            and self.run_date == other.run_date
            and self.block_id == other.block_id
        )

    def __hash__(self) -> int:
        return hash((self.block_id, self.run_date))

    def __lt__(self, other) -> bool:
        """
        Determines whether this run is less than a given object. The comparison
        is based on the run dates, or the block IDs if the dates are equal.
        """
        if not isinstance(other, Run):
            return NotImplemented

        return (self.run_date, self.block_id) < (other.run_date, other.block_id)