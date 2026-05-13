from domain.Bus import Bus
from domain.Fleet import Fleet
import customtkinter as ctk
from domain.Run import Run
from ui.AddBusFrame import AddBusFrame
from ui.AddRunFrame import AddRunFrame
from ui.MenuFrame import MenuFrame
from ui.ViewFleetFrame import ViewFleetFrame
from ui.ViewRunsFrame import ViewRunsFrame
from utilities.InvariantHelper import require_not_none, require_state
from persistence import BusPersistence, RunPersistence


class FleetController:
    """
    Changes the state of the domain model in response to events in the UI such
    as adding/removing buses and adding runs.
    """

    def __init__(self, app: ctk.CTk):
        require_not_none(app, "App should not be None.")

        self.fleet = Fleet()
        for bus in BusPersistence.load_all_buses():
            self.fleet.add_bus(bus)

        self.menu_frame = MenuFrame(app, self)
        self.view_fleet_frame = ViewFleetFrame(app, self.fleet, self)
        self.view_runs_frame = ViewRunsFrame(app, self.fleet, self)
        self.add_bus_frame = AddBusFrame(app, self.fleet, self)
        self.add_run_frame = AddRunFrame(app, self.fleet, self)

        self.curr_frame = self.view_fleet_frame

        self.menu_frame.pack(pady=5)
        self.curr_frame.pack(anchor="nw")

    def switch_to_add_bus_frame(self):
        self._switch_main_frame(self.add_bus_frame)

    def switch_to_add_run_frame(self):
        self._switch_main_frame(self.add_run_frame)

    def switch_to_view_fleet_frame(self):
        self._switch_main_frame(self.view_fleet_frame)

    def switch_to_view_runs_frame(self):
        self._switch_main_frame(self.view_runs_frame)

    def add_bus(self, bus: Bus) -> None:
        """
        Adds a given bus to this fleet in response to a UI event.

        :param bus: the bus to add to this fleet.
        """
        require_not_none(bus, "Bus should not be None.")

        self.fleet.add_bus(bus)

        BusPersistence.save_bus(bus)

    def remove_bus(self, bus: Bus) -> None:
        """
        Removes a given bus from this fleet in response to a UI event.

        :param bus: the bus to remove from this fleet.
        """
        require_not_none(bus, "Bus should not be None.")

        self.fleet.remove_bus(bus)

        BusPersistence.delete_bus(bus)

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

        RunPersistence.save_run(run, bus)

    def remove_run_from_bus(self, bus: Bus, run: Run) -> None:
        """
        Removes a given run from a given bus in response to a UI event. Assumes
        that the run exists for the given bus.

        :param bus: the bus to which to remove a run.
        :param run: the run to remove from the given bus.
        """
        require_not_none(bus, "Bus should not be None.")
        require_not_none(run, "Run should not be None.")
        require_state(bus in self.fleet.buses.values(), "Bus should be in the fleet.")

        bus.remove_run(run)

        RunPersistence.delete_run(run)

    def _switch_main_frame(self, next_frame: ctk.CTkFrame):
        """
        Sets the main frame in the application's window.

        :param next_frame: the frame to display as the main frame.
        """
        self.curr_frame.pack_forget()
        self.curr_frame = next_frame
        self.curr_frame.pack(anchor="n")


