from domain.Bus import Bus
from domain.Fleet import Fleet
import customtkinter as ctk
from domain.Run import Run
from ui.AddBusFrame import AddBusFrame
from ui.ViewFleetFrame import ViewFleetFrame
from utilities.InvariantHelper import require_not_none, require_state


class FleetController:
    """
    Changes the state of the domain model in response to events in the UI such
    as adding/removing buses and adding runs.
    """

    def __init__(self, app: ctk.CTk):
        require_not_none(app, "App should not be None.")

        self.fleet = Fleet()

        self.add_bus_frame = AddBusFrame(app, self.fleet, self)
        self.view_fleet_frame = ViewFleetFrame(app, self.fleet, self)

        self.add_bus_frame.pack(anchor="nw")
        self.view_fleet_frame.pack(anchor="nw")

    def add_bus(self, bus: Bus) -> None:
        """
        Adds a given bus to this fleet in response to a UI event.

        :param bus: the bus to add to this fleet.
        """
        require_not_none(bus, "Bus should not be None.")
        self.fleet.add_bus(bus)

    def remove_bus(self, bus: Bus) -> None:
        """
        Removes a given bus from this fleet in response to a UI event.

        :param bus: the bus to remove from this fleet.
        """
        require_not_none(bus, "Bus should not be None.")
        self.fleet.remove_bus(bus)

    def add_run_to_bus(self, bus: Bus, run: Run) -> None:
        """
        Adds a given run to a given bus in response to a UI event. Assumes
        that the bus exists in this fleet.

        :param bus: the bus to which to add a run.
        :param run: the run to add to the given bus.
        """
        require_not_none(bus, "Bus should not be None.")
        require_not_none(run, "Run should not be None.")
        require_state(bus in self.fleet.buses.values(), "Bus should be in the fleet.")
        bus.add_run(run)