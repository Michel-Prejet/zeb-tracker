from dataclasses import dataclass
from domain.bus import Bus
from domain.run import Run
from utilities.InvariantHelper import require_not_none
from datetime import date


@dataclass
class RunAssignment:
    """
    Represents a run paired with the bus that completed it.
    """
    def __init__(self, run: Run, bus: Bus):
        require_not_none(run, "Run should not be None.")
        require_not_none(bus, "Bus should not be None.")

        self.run = run
        self.bus = bus

    @property
    def date(self) -> date:
        return self.run.run_date

    @property
    def tracking_num(self) -> int:
        return self.bus.tracking_num

    @property
    def block_id(self) -> str:
        return self.run.block_id

    def __eq__(self, other) -> bool:
        """
        Determines whether a given object is equal to this run assignment. A
        run assignment is equal to another run assignment if they have the
        same run and the same bus.
        """
        return (
            isinstance(other, RunAssignment)
            and self.run == other.run
            and self.bus == other.bus
        )