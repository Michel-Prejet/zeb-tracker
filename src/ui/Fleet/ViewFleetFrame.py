from datetime import datetime
from tkinter import messagebox
import customtkinter as ctk
from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from ui.Fleet.LocationInfoDialog import LocationInfoDialog
from ui.Fleet.Search.BusSearchFilters import SearchFilterType, build_search_filter_function
from ui.Fleet.Search.BusSearchFrame import BusSearchFrame
from ui.Pagination.Paginatable import Paginatable
from ui.Pagination.PaginationFrame import PaginationFrame
from ui.UIConstants import LARGE_TITLE_FONT, PADDING_MEDIUM, APP_WIDTH, PADDING_LARGE, SMALL_TITLE_FONT, \
    WIDE_ROW_BUTTON_WIDTH, WIDE_ROW_BUTTON_HEIGHT, MEDIUM_BUTTON_WIDTH, MEDIUM_BUTTON_HEIGHT
from utilities.DateTimeHelper import format_date, format_datetime
from utilities.InvariantHelper import require_not_none


UNKNOWN_DATE_PLACEHOLDER = "never"
UNKNOWN_LOCATION_PLACEHOLDER = "No location information"

LOCATION_INFO_FONT_SIZE = 13
LOCATION_INFO_FONT_SIZE_HOVER = 14

BUSES_PER_PAGE = 15

SCROLLABLE_LIST_DIMENSIONS = (APP_WIDTH, 650)
SCROLLABLE_LIST_WIDTH, SCROLLABLE_LIST_HEIGHT = SCROLLABLE_LIST_DIMENSIONS

class ViewFleetFrame(ctk.CTkFrame, Listener, Paginatable):
    """
    Frame displaying the list of buses in a given fleet, including their
    tracking number, model info, the date of their last run, and a "remove"
    button. A search function is displayed above the bus list, including
    an input field in which the user can enter a filter string, as well as
    a dropdown menu to select a filter type and a button to submit the search.
    """

    def __init__(self, app: ctk.CTk, fleet: Fleet, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(fleet, "Fleet should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)

        self.app = app
        self.controller = controller
        self.fleet = fleet
        self.fleet.register_listener(self)

        self.buses = fleet.sorted_buses()
        self.curr_search_filter = lambda bus_list: bus_list
        self.curr_page = 1

        self._create_header()
        self._create_search_area()
        self._create_location_fetch_area()
        self._create_pagination_area()
        self._initialize_scrollable_list()

        self.notify()

    def notify(self) -> None:
        """
        Refreshes the list of buses and the page information in response to a
        change in the state of the fleet. Clears the old scrollable list of
        buses and reconstructs it, applying the current search filter and
        appending all necessary labels and buttons.
        """
        self._clear_scrollable_list()

        self._apply_search_filter()

        self.pagination_frame.update_page_info(self.curr_page)

        self._show_no_buses_in_list_if_empty()

        self._create_bus_list()

    def show_fetching_location(self) -> None:
        """
        Updates the UI to show elements relevant to the location scan.
        Shows a message telling the user that the system is fetching bus
        locations, initializing the displayed progress of the scan to 0%.
        Adds a button to the screen to cancel the scan.
        """
        self.location_fetch_button.configure(state="disabled")
        self._show_location_fetch_feedback(percentage=0)

        self._show_cancel_scan_button()

        self.notify()

    def update_location_fetch_progress(self, completed_stops: int, total_stops: int) -> None:
        """
        Updates the progress of the location scan displayed in the UI based on
        the given values. Progress is calculated by dividing the number of
        completed stops by the total number of stops.

        :param completed_stops: the number of stops that have been scanned.
        :param total_stops: the total number of stops to scan.
        """
        self._show_location_fetch_feedback(round(completed_stops / total_stops * 100))

    def show_location_fetch_finished(self) -> None:
        """
        Updates the UI to remove elements used for the location scan. Removes
        the 'Fetching location' message and the 'Cancel' button.
        """
        self._show_location_fetch_feedback() # Clears the field
        self.location_fetch_button.configure(state="enabled")

        self._hide_cancel_scan_button()

        self.notify()

    def update_location_fetch_query_time(self, query_time: datetime) -> None:
        """
        Updates the query time of the last location scan to the given value.

        :param query_time: a datetime object representing the query time of
        the last location scan.
        """
        self._show_location_fetch_feedback(query_time=query_time)

    def handle_enter(self, event=None) -> None:
        """
        Event handler for when the user presses the Enter key.
        """
        self._submit_search()

    def handle_left_arrow(self, event=None) -> None:
        """
        Event handler for when the user presses the left arrow key.
        """
        self.prev_page()

    def handle_right_arrow(self, event=None) -> None:
        """
        Event handler for when the user presses the right arrow key.
        """
        self.next_page()

    def next_page(self) -> None:
        if self.curr_page + 1 <= self.pagination_frame.num_pages():
            self.curr_page += 1
            self._refresh_and_scroll_to_top()

    def prev_page(self) -> None:
        if self.curr_page > 1:
            self.curr_page -= 1
            self._refresh_and_scroll_to_top()

    def first_page(self) -> None:
        self.curr_page = 1
        self._refresh_and_scroll_to_top()

    def last_page(self) -> None:
        self.curr_page = self.pagination_frame.num_pages()
        self._refresh_and_scroll_to_top()

    def _refresh_and_scroll_to_top(self) -> None:
        self.notify()
        self.scrollable_list._parent_canvas.yview_moveto(0)

    def _create_header(self) -> None:
        ctk.CTkLabel(
            self,
            text="Fleet",
            font=LARGE_TITLE_FONT
        ).pack()

    def _create_search_area(self) -> None:
        self.search_frame = BusSearchFrame(
            parent=self,
            submit_search=self._submit_search,
            reset_search=self._reset_search,
            show_only_active=self._show_only_active
        )
        self.search_frame.pack(
            anchor="nw",
            padx=PADDING_MEDIUM,
            pady=PADDING_MEDIUM
        )

    def _create_location_fetch_area(self) -> None:
        self.location_fetch_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.location_fetch_frame.pack(
            anchor="w",
            padx=PADDING_MEDIUM,
            pady=PADDING_MEDIUM
        )

        self._create_location_fetch_button()
        self._create_location_fetch_feedback_area()

        self.cancel_scan_button = None

    def _create_location_fetch_button(self) -> None:
        self.location_fetch_button = ctk.CTkButton(
            self.location_fetch_frame,
            text="Fetch location information",
            command=self.controller.update_bus_locations
        )
        self.location_fetch_button.pack(anchor="nw", side="left")

    def _create_location_fetch_feedback_area(self) -> None:
        self.location_fetch_feedback = ctk.CTkLabel(
            self.location_fetch_frame,
            text=""
        )
        self.location_fetch_feedback.pack(
            anchor="nw",
            padx=PADDING_LARGE,
            side="left"
        )

    def _create_pagination_area(self) -> None:
        self.pagination_frame = PaginationFrame(
            parent=self,
            item_name="buses",
            items_per_page=BUSES_PER_PAGE,
            get_num_items=lambda: len(self.buses)
        )
        self.pagination_frame.pack(
            anchor="nw",
            padx=PADDING_MEDIUM,
            pady=PADDING_MEDIUM
        )

    def _initialize_scrollable_list(self) -> None:
        self.scrollable_list = ctk.CTkScrollableFrame(
            self,
            width=SCROLLABLE_LIST_WIDTH,
            height=SCROLLABLE_LIST_HEIGHT
        )
        self.scrollable_list.pack()

    def _clear_scrollable_list(self) -> None:
        for child in self.scrollable_list.winfo_children():
            child.destroy()

    def _apply_search_filter(self) -> None:
        all_buses = self.fleet.sorted_buses()
        self.buses = self.curr_search_filter(all_buses)

    def _show_no_buses_in_list_if_empty(self) -> None:
        if len(self.buses) == 0:
            ctk.CTkLabel(
                self.scrollable_list,
                text="No buses to display."
            ).pack(anchor="nw")

    def _create_bus_list(self) -> None:
        start_bus_index = (self.curr_page - 1) * BUSES_PER_PAGE
        end_bus_index = start_bus_index + BUSES_PER_PAGE

        for bus in self.buses[start_bus_index:end_bus_index]:
            row = ctk.CTkFrame(self.scrollable_list)
            row.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)

            self._add_bus_data_to_row(bus, row)
            self._add_bus_location_info_to_row(bus, row)
            self._add_remove_button_to_row(bus, row)

    def _add_bus_data_to_row(self, bus: Bus, row: ctk.CTkFrame) -> None:
        self._add_row_data(
            text=f"{bus.tracking_num}",
            row=row,
            font=SMALL_TITLE_FONT
        )

        self._add_row_data(
            text=f" {bus.year} {bus.model}",
            row=row
        )

        self._add_row_data(
            text=f"Last seen: {last_run_date_to_str(bus)}",
            row=row
        )

    def _add_row_data(self, text: str, row: ctk.CTkFrame,
                      font: ctk.CTkFont | tuple | None = None) -> None:
        ctk.CTkLabel(
            row,
            text=text,
            font=font or ctk.CTkFont()
        ).pack(side="left", padx=PADDING_MEDIUM)

    def _add_bus_location_info_to_row(self, bus: Bus, row: ctk.CTkFrame) -> None:
        info = ctk.CTkLabel(
            row,
            text=UNKNOWN_LOCATION_PLACEHOLDER,
            text_color="grey"
        )

        if bus.location_info is not None:
            info.configure(
                text=self._get_bus_location_info_label(bus),
                text_color="green",
                font=ctk.CTkFont(size=LOCATION_INFO_FONT_SIZE)
            )
            
            self._bind_label_to_show_location_info_popup_on_click(info, bus)
            self._bind_label_to_change_font_size_on_hover(info)

        info.pack(side="left", padx=PADDING_MEDIUM)

    def _get_bus_location_info_label(self, bus: Bus) -> str:
        require_not_none(bus.location_info,"Bus should contain location info.")

        label = f"🟢 {bus.location_info.route} "

        if bus.location_info.block_id is not None:
            label += f"({bus.location_info.block_id}) "

        return label

    def _bind_label_to_show_location_info_popup_on_click(self, location_info_label: ctk.CTkLabel, bus: Bus) -> None:
        location_info_label.bind(
            "<Button-1>",
            lambda e, b=bus: LocationInfoDialog(self.app, b)
        )

    def _bind_label_to_change_font_size_on_hover(self, location_info_label: ctk.CTkLabel) -> None:
        location_info_label.bind(
            "<Enter>",
            lambda e, l=location_info_label: l.configure(font=ctk.CTkFont(size=LOCATION_INFO_FONT_SIZE_HOVER))
        )
        location_info_label.bind(
            "<Leave>",
            lambda e, l=location_info_label: l.configure(font=ctk.CTkFont(size=LOCATION_INFO_FONT_SIZE))
        )

    def _add_remove_button_to_row(self, bus: Bus, row: ctk.CTkFrame) -> None:
        ctk.CTkButton(
            row,
            text="Remove",
            width=WIDE_ROW_BUTTON_WIDTH,
            height=WIDE_ROW_BUTTON_HEIGHT,
            command=lambda b=bus: self._confirm_remove_bus(b)
        ).pack(side="right", padx=PADDING_MEDIUM)

    def _confirm_remove_bus(self, bus: Bus) -> None:
        """
        Displays a pop-up window asking the user to confirm that they would
        like to remove a bus from the fleet. Removes the bus if the user
        selects Yes.

        :param bus: the bus to remove from the fleet if the user selects Yes.
        """
        confirmed = messagebox.askyesno(
            "Remove bus",
            f"Are you sure you want to delete bus {bus.tracking_num}?"
        )

        if confirmed:
            self.controller.remove_bus(bus)

    def _reset_search(self) -> None:
        """
        Reconstructs the bus list with all filters removed and goes back
        to page 1.
        """
        self.curr_page = 1
        self.curr_search_filter = lambda bus_list: bus_list
        self.notify()

        self.search_frame.reset()

    def _submit_search(self) -> None:
        """
        Filters the bus list based on the input provided in the search entry
        field, the search filter type menu, and the "Active buses only"
        checkbox. Takes no action if the search entry is empty or only whitespace.
        Does not validate input; invalid search filters will simply result in
        zero results.
        """
        search_filter = self.search_frame.get_input()
        search_filter_type: SearchFilterType = self.search_frame.get_search_filter_selection()
        show_only_active = self.search_frame.get_show_only_active_selection()

        self.curr_search_filter = build_search_filter_function(
            search_filter,
            search_filter_type,
            show_only_active
        )

        self.curr_page = 1

        self.notify()

    def _show_only_active(self) -> None:
        self.curr_page = 1
        self._submit_search()

    def _show_location_fetch_feedback(self, percentage: int | None = None,
                                      query_time: datetime | None = None) -> None:
        """
        Sets the location fetch feedback field based on the given parameters.
        If a percentage is provided, displays a message telling the user that
        location fetch is in progress (with the given percentage).
        If a query time is provided, displays a message telling the user that
        the last location fetch was at that time.
        If nothing is provided, the field is cleared.
        """
        if percentage is not None:
            self.location_fetch_feedback.configure(
                text=f"Fetching bus locations ({percentage}%)"
            )
        elif query_time is not None:
            self.location_fetch_feedback.configure(
                text=f"Last fetch: {format_datetime(query_time)}"
            )
        else:
            self.location_fetch_feedback.configure(text="")

    def _show_cancel_scan_button(self) -> None:
        self.cancel_scan_button = ctk.CTkButton(
            self.location_fetch_frame,
            text="Cancel",
            width=MEDIUM_BUTTON_WIDTH,
            height=MEDIUM_BUTTON_HEIGHT,
            fg_color="transparent",
            command=self.controller.cancel_update_bus_locations
        )
        self.cancel_scan_button.pack(anchor="nw", side="left")

    def _hide_cancel_scan_button(self) -> None:
        if self.cancel_scan_button is not None:
            self.cancel_scan_button.pack_forget()
            self.cancel_scan_button = None

def last_run_date_to_str(bus: Bus) -> str:
    """
    :bus: the bus for which to get the last run date as a string.
    :return: the last run completed by the given bus as a string of the form
    MONTH DAY, YEAR (e.g. May 2, 2026) or "never" if the given bus hasn't
    completed any runs.
    """
    if bus.last_run() is None:
        return UNKNOWN_DATE_PLACEHOLDER
    return format_date(bus.last_run().run_date)


