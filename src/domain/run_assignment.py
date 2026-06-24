from dataclasses import dataclass
from domain.bus import Bus
from domain.run import Run
from utilities.InvariantHelper import require_not_none


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

