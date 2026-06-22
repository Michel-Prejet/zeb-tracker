from datetime import datetime
from domain.Bus import Bus
from domain.Fleet import Fleet
import customtkinter as ctk
from domain.InferredRunList import InferredRunList
from domain.Run import Run
from ui.fleet.AddBusFrame import AddBusFrame
from ui.fleet.ErrorLog import ErrorLog
from ui.runs.AddRunFrame import AddRunFrame
from ui.csv_export.CSVExportDialog import CSVExportDialog
from ui.MenuFrame import MenuFrame
from ui.fleet.ViewFleetFrame import ViewFleetFrame
from ui.runs.ViewRunsFrame import ViewRunsFrame
from ui.UIConstants import PADDING_MEDIUM
from utilities.InvariantHelper import require_not_none, require_state
from persistence import BusPersistence, RunPersistence
from threading import Thread
from logic.BusLocationUpdater import update_bus_locations
from logic.RunFinder import infer_runs_from_location_info
from utilities.live_tracker.LiveBusTracker import LiveBusTracker


class FleetController:
    """
    Changes the state of the domain model in response to events in the UI such
    as adding/removing buses and adding runs.
    """

    def __init__(self, app: ctk.CTk):
        require_not_none(app, "App should not be None.")

        self.app = app

        self._initialize_and_load_domain_model()
        self._initialize_location_tracker()
        self._create_frames()
        self._bind_hotkeys()
        self._display_initial_frame()

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

    def add_inferred_run_to_fleet(self, run: Run, bus: Bus) -> None:
        """
        Adds a given run from the inferred run list to a given bus in the fleet
        in response to a UI event.

        :param run: the run to add to the given bus from the inferred run list.
        :param bus: the bus to which to add the run.
        """
        require_not_none(run, "Run should not be None.")
        require_not_none(bus, "Bus should not be None.")

        success = self.inferred_runs.add_to_fleet(run, bus)

        if success:
            RunPersistence.save_run(run, bus)

    def remove_inferred_run(self, run: Run, bus: Bus) -> None:
        """
        Removes a given run from the inferred run list in response to a UI event

        :param run:
        :param bus:
        :return:
        """
        require_not_none(run, "Run should not be None.")
        require_not_none(bus, "Bus should not be None.")

        self.inferred_runs.remove(run, bus)

    def add_all_inferred_runs_to_fleet(self) -> None:
        """
        Adds all inferred runs to the fleet in response to a UI event.
        """
        added_runs = self.inferred_runs.add_all_to_fleet()

        for run, bus in added_runs:
            RunPersistence.save_run(run, bus)

    def update_bus_locations(self) -> None:
        """
        Fetches location information from the Winnipeg Transit API
        concurrently and then updates the location information of all
        buses in this fleet for which information was found. Takes no action
        if another location fetch is still active.
        """
        if self.location_fetch_active:
            return

        self.location_fetch_active = True
        self.view_fleet_frame.show_fetching_location()

        thread = Thread(target=self._update_bus_locations_background, daemon=True)
        thread.start()

    def start_polling_bus_locations(self, wait_time_minutes: int=30) -> None:
        """
        Fetches location information from the Winnipeg Transit API and updates
        bus location information repeatedly until the user cancels the location
        fetch.

        :param wait_time_minutes: the number of minutes to wait between each
        location fetch.
        """
        self.polling_locations = True
        self._poll_bus_locations(wait_time_minutes)

    def stop_polling_bus_locations(self) -> None:
        self.polling_locations = False
        self.cancel_update_bus_locations()

    def cancel_update_bus_locations(self) -> None:
        """
        Cancels any ongoing bus location scan.
        """
        if self.tracker is not None:
            self.tracker.cancel_stop_scan()

    def switch_to_add_bus_frame(self) -> None:
        self._switch_main_frame(self.add_bus_frame)

    def switch_to_add_run_frame(self) -> None:
        self._switch_main_frame(self.add_run_frame)

    def switch_to_view_fleet_frame(self) -> None:
        self._switch_main_frame(self.view_fleet_frame)

    def switch_to_view_runs_frame(self) -> None:
        self._switch_main_frame(self.view_runs_frame)

    def show_csv_export_dialog(self) -> None:
        if self.csv_export_dialog is None:
            self.csv_export_dialog = CSVExportDialog(self.app, self.fleet)
        else:
            self.csv_export_dialog.deiconify()

        self.csv_export_dialog.lift()
        self.csv_export_dialog.focus_force()

    def _show_error_log_dialog(self, error_messages: list[str]) -> None:
        if self.error_log_dialog is None:
            self.error_log_dialog = ErrorLog(self.app, error_messages, self)
        else:
            self.error_log_dialog.deiconify()

        self.error_log_dialog.lift()
        self.error_log_dialog.focus_force()

    def _initialize_and_load_domain_model(self) -> None:
        self.fleet = Fleet()
        for bus in BusPersistence.load_all_buses():
            self.fleet.add_bus(bus)

    def _initialize_location_tracker(self) -> None:
        self.tracker = None
        self.inferred_runs = InferredRunList(self.fleet)
        self.location_fetch_active = False
        self.polling_locations = False

    def _create_frames(self) -> None:
        self.menu_frame = MenuFrame(self.app, self)
        self.view_fleet_frame = ViewFleetFrame(self.app, self.fleet, self)
        self.view_runs_frame = ViewRunsFrame(self.app, self.fleet, self)
        self.add_bus_frame = AddBusFrame(self.app, self)
        self.add_run_frame = AddRunFrame(self.app, self.inferred_runs, self)
        self.csv_export_dialog = None
        self.error_log_dialog = None

        self.curr_frame = self.view_fleet_frame

    def _bind_hotkeys(self) -> None:
        self.app.bind("<Return>", lambda _: self._handle_hotkey("handle_enter"))
        self.app.bind("<Left>", lambda _: self._handle_hotkey("handle_left_arrow"))
        self.app.bind("<Right>", lambda _: self._handle_hotkey("handle_right_arrow"))

    def _display_initial_frame(self) -> None:
        self.menu_frame.pack(pady=PADDING_MEDIUM)
        self.curr_frame.pack(anchor="nw")

    def _switch_main_frame(self, next_frame: ctk.CTkFrame):
        """
        Sets the main frame in the application's window.

        :param next_frame: the frame to display as the main frame.
        """
        self.curr_frame.pack_forget()
        self.curr_frame = next_frame
        self.curr_frame.pack(anchor="n")

    def _handle_hotkey(self, handler_name: str, event=None) -> None:
        """
        Responds to the user pressing a hotkey. Calls an event handler in
        the current frame, if such an event handler exists. Otherwise, no
        action is taken.

        :param handler_name: the name of the handler to call.
        :param event: the Tkinter event to handle (None by default).
        """
        if self.curr_frame is not None:
            handler = getattr(self.curr_frame, handler_name, None)

            if callable(handler):
                handler(event)

    def _update_bus_locations_background(self) -> None:
        """
        Creates a live bus tracker object and starts the stop scan. Catches
        any exceptions that might occur and stops the scan early.
        """
        try:
            if self.tracker is None:
                self.tracker = LiveBusTracker(self.view_fleet_frame.update_location_fetch_progress)
                self.tracker.read_gtfs()

            success = self.tracker.scan_stops()
            self.app.after(0, self._apply_bus_locations, success)
        except Exception as e:
            self.tracker.log_error(e)
            self.cancel_update_bus_locations()
            self.app.after(
                0,
                self._complete_location_fetch
            )

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

        self._complete_location_fetch()
        if success:
            self.view_fleet_frame.update_location_fetch_query_time(datetime.now())

    def _poll_bus_locations(self, wait_time_minutes: int) -> None:
        SECONDS_PER_MINUTE = 60
        MILLISECONDS_PER_SECOND = 1000

        if not self.polling_locations:
            return

        self.update_bus_locations()

        self.app.after(
            wait_time_minutes * SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND,
            lambda: self._poll_bus_locations(wait_time_minutes)
        )

    def _complete_location_fetch(self) -> None:
        self.location_fetch_active = False
        self.view_fleet_frame.show_location_fetch_finished()

        err_messages = self.tracker.get_error_messages()
        if len(err_messages) > 0:
            self._show_error_log_dialog(err_messages)
            self.error_log_dialog = None





