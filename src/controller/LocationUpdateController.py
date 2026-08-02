from datetime import datetime
from threading import Thread
from typing import Callable
import customtkinter as ctk
from constants.app_constants import SECONDS_PER_MINUTE, MILLISECONDS_PER_SECOND, DEFAULT_POLLING_INTERVAL_MINUTES
from domain.fleet import Fleet
from domain.inferred_run_list import InferredRunList
from logic.run_finder import infer_runs_from_location_info
from ui.fleet.view_fleet_frame import ViewFleetFrame
from utilities.invariant_helper import require_not_none
from utilities.live_tracker.live_bus_tracker import LiveBusTracker
from logic.bus_location_updater import update_bus_locations


class LocationUpdateController:
    """
    Coordinates the location fetch process in the app, including GTFS parsing and
    API requests on a separate thread, polling mode, cancelling an ongoing location
    fetch, maintaining an error log, and updating the UI.
    """

    def __init__(self, app: ctk.CTk, fleet: Fleet, inferred_runs: InferredRunList, view_fleet_frame: ViewFleetFrame,
                 show_error_log_dialog: Callable[[list[str]], None]) -> None:
        require_not_none(app, "App should not be None.")
        require_not_none(fleet, "Fleet should not be None.")
        require_not_none(inferred_runs, "Inferred run list should not be None.")
        require_not_none(view_fleet_frame, "View fleet frame should not be None.")
        require_not_none(
            show_error_log_dialog,
            "Function to show error log dialog should not be None."
        )

        self.app = app
        self.fleet = fleet
        self.inferred_runs = inferred_runs
        self.view_fleet_frame = view_fleet_frame
        self.show_error_log_dialog = show_error_log_dialog

        self.tracker = None
        self.active = False
        self.polling_mode = False

    def start_location_fetch_single(self) -> None:
        """
        Runs one location fetch. Gathers location information from the Winnipeg
        Transit API on a separate thread. If this process was successful, the
        data is used to update bus location information in the fleet and add
        runs to the inferred run list. Any errors are saved in an error log
        that is displayed after the process has terminated.
        """
        if self.active:
            return
        self.active = True

        self.view_fleet_frame.show_fetching_location()

        # Gather info from the API/GTFS in a separate thread
        t = Thread(
            target=self._get_location_info_from_tracker,
            daemon=True
        )
        t.start()

    def start_location_fetch_polling(self, downtime_minutes: int) -> None:
        """
        Runs location fetches periodically according to the given downtime. The
        process must be cancelled for it to terminate.

        :param downtime_minutes: the number of minutes between the beginning of
        each location fetch.
        """
        if self.polling_mode:
            return

        self.polling_mode = True
        self._repeat_location_fetch_until_cancel(downtime_minutes)

    def cancel_location_fetch(self) -> None:
        """
        Tells the tracker to cancel all remaining stop scans in order to
        prematurely terminate the current location fetch.
        """
        if self.tracker is not None:
            self.tracker.cancel_stop_scan()
        self.polling_mode = False

    def _get_location_info_from_tracker(self) -> None:
        try:
            self._create_tracker_if_none()

            scan_completed_successfully = self.tracker.scan_stops()
            if scan_completed_successfully:
                self.app.after(0, self._complete_successful_location_fetch)
            else:
                self.app.after(0, self._complete_cancelled_location_fetch)
        except Exception as e:
            if self.tracker is not None:
                self.tracker.log_error(e)

            self.cancel_location_fetch()
            self.app.after(0, self._complete_cancelled_location_fetch)

    def _create_tracker_if_none(self) -> None:
        if self.tracker is None:
            self.tracker = LiveBusTracker(self.view_fleet_frame.update_location_fetch_progress)
            self.tracker.read_gtfs()

    def _complete_successful_location_fetch(self) -> None:
        update_bus_locations(self.fleet, self.tracker)
        infer_runs_from_location_info(self.inferred_runs)

        self._set_inactive()
        self._handle_errors()

        self.view_fleet_frame.update_location_fetch_query_time(datetime.now())

    def _complete_cancelled_location_fetch(self) -> None:
        self._set_inactive()
        self._handle_errors()

    def _set_inactive(self) -> None:
        self.active = False
        self.view_fleet_frame.show_location_fetch_finished()

    def _handle_errors(self) -> None:
        if self.tracker is None:
            return

        err_messages = self.tracker.get_error_messages()
        if err_messages:
            self.show_error_log_dialog(err_messages)

    def _repeat_location_fetch_until_cancel(self, downtime_minutes: int) -> None:
        if not self.polling_mode:
            return

        self.start_location_fetch_single()

        self.app.after(
            downtime_minutes * SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND,
            lambda: self._repeat_location_fetch_until_cancel(downtime_minutes)
        )


