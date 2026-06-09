from datetime import datetime
from domain.Bus import Bus
from domain.Fleet import Fleet
import customtkinter as ctk
from domain.InferredRunList import InferredRunList
from domain.Run import Run
from ui.AddBusFrame import AddBusFrame
from ui.AddRunFrame import AddRunFrame
from ui.CSVExportDialog import CSVExportDialog
from ui.MenuFrame import MenuFrame
from ui.ViewFleetFrame import ViewFleetFrame
from ui.ViewRunsFrame import ViewRunsFrame
from utilities.InvariantHelper import require_not_none, require_state
from persistence import BusPersistence, RunPersistence
from threading import Thread
from utilities.LocationInfoHelper import update_bus_locations
from utilities.RunFinder import infer_runs_from_location_info
from utilities.live_tracker.LiveBusTracker import LiveBusTracker


class FleetController:
    """
    Changes the state of the domain model in response to events in the UI such
    as adding/removing buses and adding runs.
    """

    def __init__(self, app: ctk.CTk):
        require_not_none(app, "App should not be None.")

        self.app = app
        self.fleet = Fleet()
        for bus in BusPersistence.load_all_buses():
            self.fleet.add_bus(bus)
        self.tracker = None
        self.inferred_runs = InferredRunList(self.fleet)

        # Initialize frames
        self.menu_frame = MenuFrame(app, self)
        self.view_fleet_frame = ViewFleetFrame(app, self.fleet, self)
        self.view_runs_frame = ViewRunsFrame(app, self.fleet, self)
        self.add_bus_frame = AddBusFrame(app, self)
        self.add_run_frame = AddRunFrame(app, self.inferred_runs, self)
        self.csv_export_dialog = None

        self.curr_frame = self.view_fleet_frame

        # Bind hotkeys
        self.app.bind("<Return>", self._handle_enter)
        self.app.bind("<Left>", self._handle_left_arrow)
        self.app.bind("<Right>", self._handle_right_arrow)

        # Show the menu and the current frame
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

    def show_csv_export_dialog(self):
        if self.csv_export_dialog is None:
            self.csv_export_dialog = CSVExportDialog(self.app, self.fleet)
        else:
            self.csv_export_dialog.deiconify()

        self.csv_export_dialog.lift()
        self.csv_export_dialog.focus_force()

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

    def add_run_to_bus(self, bus_tracking_num: int, run: Run) -> None:
        """
        Adds a given run to a given bus in response to a UI event. Assumes
        that the bus exists in this fleet.

        :param bus_tracking_num: the tracking number of the bus to which to add a run.
        :param run: the run to add to the given bus.
        """
        require_not_none(bus_tracking_num, "Bus tracking number should not be None.")
        require_not_none(run, "Run should not be None.")
        require_state(bus_tracking_num in self.fleet.buses.keys(), "Bus should be in the fleet.")

        bus = self.fleet.get_bus(bus_tracking_num)
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

    def add_inferred_run_for_bus(self, tracking_num: int) -> None:
        """
        Adds a run to the fleet from the inferred run list in response to a UI
        event. The run is retrieved from the given bus tracking number and
        added to the corresponding bus.

        :param tracking_num: the tracking number of the bus to which to add
        an inferred run.
        """
        require_not_none(tracking_num, "Bus tracking number should not be None.")

        added_run = self.inferred_runs.add_to_fleet(tracking_num)

        if added_run is not None:
            RunPersistence.save_run(added_run[0], added_run[1])

    def add_all_inferred_runs(self) -> None:
        """
        Adds all inferred runs to the fleet in response to a UI event.
        """
        added_runs = self.inferred_runs.add_all_to_fleet()

        for run in added_runs:
            RunPersistence.save_run(run[0], run[1])

    def update_bus_locations(self) -> None:
        """
        Fetches location information from the Winnipeg Transit API
        concurrently and then updates the location information of all
        buses in this fleet for which information was found.
        """
        self.view_fleet_frame.show_fetching_location()
        thread = Thread(target=self._update_bus_locations_background, daemon=True)
        thread.start()

    def cancel_update_bus_locations(self) -> None:
        """
        Cancels any ongoing bus location scan.
        """
        if self.tracker is not None:
            self.tracker.cancel_stop_scan()

    def _update_bus_locations_background(self) -> None:
        """
        Creates a live bus tracker object and starts the stop scan. Catches
        any exceptions that might occur and stops the scan early.
        """
        try:
            if self.tracker is None:
                self.tracker = LiveBusTracker(self.view_fleet_frame.update_location_fetch_progress)
            success = self.tracker.scan_stops()
            self.app.after(0, self._apply_bus_locations, success)
        except Exception as e:
            print(f"Error updating locations: {e}")
            self.view_fleet_frame.show_location_fetch_finished()

    def _apply_bus_locations(self, success: bool) -> None:
        """
        Updates the UI to indicate that the stop scan has finished, and if
        the scan was successful, updates all bus locations and displays the
        query time.

        :param success: whether the stop scan was successful.
        """
        if success:
            update_bus_locations(self.fleet, self.tracker)
            infer_runs_from_location_info(self.inferred_runs)

        self.view_fleet_frame.show_location_fetch_finished()

        if success:
            self.view_fleet_frame.update_location_fetch_query_time(datetime.now())

    def _switch_main_frame(self, next_frame: ctk.CTkFrame):
        """
        Sets the main frame in the application's window.

        :param next_frame: the frame to display as the main frame.
        """
        self.curr_frame.pack_forget()
        self.curr_frame = next_frame
        self.curr_frame.pack(anchor="n")

    def _handle_enter(self, event=None) -> None:
        """
        Responds to the user pressing the Enter key. Calls an event handler
        in the current frame, if such an event handler exists. Otherwise,
        no action is taken.

        :param event: the Tkinter event to handle (None by default).
        """

        if self.curr_frame is not None:
            enter_handler = getattr(self.curr_frame, "handle_enter", None)

            if callable(enter_handler):
                self.curr_frame.handle_enter(event)

    def _handle_left_arrow(self, event=None) -> None:
        """
        Responds to the user pressing the left arrow key. Calls an event handler
        in the current frame, if such an event handler exists. Otherwise, no
        action is taken.

        :param event: the Tkinter event to handle (None by default).
        """

        if self.curr_frame is not None:
            left_arrow_handler = getattr(self.curr_frame, "handle_left_arrow", None)

            if callable(left_arrow_handler):
                self.curr_frame.handle_left_arrow(event)

    def _handle_right_arrow(self, event=None) -> None:
        """
        Responds to the user pressing the right arrow key. Calls an event handler
        in the current frame, if such an event handler exists. Otherwise, no
        action is taken.

        :param event: the Tkinter event to handle (None by default).
        """

        if self.curr_frame is not None:
            right_arrow_handler = getattr(self.curr_frame, "handle_right_arrow", None)

            if callable(right_arrow_handler):
                self.curr_frame.handle_right_arrow(event)



