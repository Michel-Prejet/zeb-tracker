from constants.app_constants import DEFAULT_POLLING_INTERVAL_MINUTES
from controller.LocationUpdateController import LocationUpdateController
from domain.bus import Bus
from domain.fleet import Fleet
import customtkinter as ctk
from domain.inferred_run_list import InferredRunList
from domain.run import Run
from domain.run_assignment import RunAssignment
from ui.fleet.add_bus_frame import AddBusFrame
from ui.fleet.error_log import ErrorLog
from ui.runs.add_run_frame import AddRunFrame
from ui.csv_export.csv_export_dialog import CSVExportDialog
from ui.menu_frame import MenuFrame
from ui.fleet.view_fleet_frame import ViewFleetFrame
from ui.runs.view_runs_frame import ViewRunsFrame
from constants.ui_constants import PADDING_MEDIUM
from utilities.invariant_helper import require_not_none
from persistence import bus_persistence, run_persistence


class FleetController:
    """
    Changes the state of the domain model in response to events in the UI such
    as adding/removing buses and adding runs.
    """

    def __init__(self, app: ctk.CTk):
        require_not_none(app, "App should not be None.")

        self.app = app

        self._initialize_and_load_domain_model()
        self._create_frames()
        self._initialize_location_tracker()
        self._bind_hotkeys()
        self._display_initial_frame()

    def add_bus(self, bus: Bus) -> None:
        """
        Adds a given bus to this fleet in response to a UI event.
        """
        require_not_none(bus, "Bus should not be None.")

        self.fleet.add_bus(bus)

        bus_persistence.save_bus(bus)

    def remove_bus(self, bus: Bus) -> None:
        """
        Removes a given bus from this fleet in response to a UI event.
        """
        require_not_none(bus, "Bus should not be None.")

        self.fleet.remove_bus(bus)

        bus_persistence.delete_bus(bus)

    def add_run_to_bus(self, bus_tracking_num: int, run: Run) -> None:
        """
        Adds a given run to a bus with a given tracking number in response to a
        UI event.
        """
        require_not_none(bus_tracking_num, "Tracking number should not be None.")
        require_not_none(run, "Run should not be None.")

        bus = self.fleet.get_bus(bus_tracking_num)
        require_not_none(bus, "Bus should not be None.")

        run_assignment = RunAssignment(run, bus)
        self.fleet.add_run(run_assignment)

        run_persistence.save_run(run_assignment)

    def remove_run_from_bus(self, run_assignment: RunAssignment) -> None:
        """
        Removes a run from a bus in a given run assignment in response to a UI event.
        """
        require_not_none(run_assignment, "Run assignment should not be None.")

        self.fleet.remove_run(run_assignment)

        run_persistence.delete_run(run_assignment.run)

    def add_inferred_run_to_fleet(self, run_assignment: RunAssignment) -> None:
        """
        Adds a given run assignment from the inferred run list to the
        corresponding bus in the fleet in response to a UI event.
        """
        require_not_none(run_assignment, "Run assignment should not be None.")

        success = self.inferred_runs.commit(run_assignment)

        if success:
            run_persistence.save_run(run_assignment)

    def remove_inferred_run(self, run_assignment: RunAssignment) -> None:
        """
        Removes a given run from the inferred run list in response to a UI event
        """
        require_not_none(run_assignment, "Run assignment should not be None.")

        self.inferred_runs.remove_inferred_run(run_assignment)

    def add_all_inferred_runs_to_fleet(self) -> None:
        """
        Adds all inferred runs to the fleet in response to a UI event.
        """
        added_runs = self.inferred_runs.commit_all()

        for run_assignment in added_runs:
            run_persistence.save_run(run_assignment)

    def start_location_fetch(self, polling_mode: bool=False,
                             downtime_minutes: int=DEFAULT_POLLING_INTERVAL_MINUTES) -> None:
        """
        Runs location fetch(es). Gathers location information from the Winnipeg
        Transit API on a separate thread. If this process was successful, the
        data is used to update bus location information in the fleet and add
        runs to the inferred run list. Any errors are saved in an error log
        that is displayed after the process has terminated.

        :param polling_mode: whether to fetch locations once or run the process
        periodically.
        :param downtime_minutes: the number of minutes between the beginning of
        each location fetch (if polling).
        """
        if polling_mode:
            self.location_update_controller.start_location_fetch_polling(downtime_minutes)
        else:
            self.location_update_controller.start_location_fetch_single()

    def cancel_location_fetch(self) -> None:
        """
        Tells the tracker to cancel all remaining stop scans in order to
        prematurely terminate the current location fetch.
        """
        self.location_update_controller.cancel_location_fetch()

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
        """
        Displays the error log dialog.
        """
        error_log_dialog = ErrorLog(self.app, error_messages)
        error_log_dialog.lift()
        error_log_dialog.focus_force()

    def _initialize_and_load_domain_model(self) -> None:
        self.fleet = Fleet()
        for bus in bus_persistence.load_all_buses():
            self.fleet.add_bus(bus)
        self.inferred_runs = InferredRunList(self.fleet)

    def _initialize_location_tracker(self) -> None:
        self.location_update_controller = LocationUpdateController(
            self.app,
            self.fleet,
            self.inferred_runs,
            self.view_fleet_frame,
            self._show_error_log_dialog
        )

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





