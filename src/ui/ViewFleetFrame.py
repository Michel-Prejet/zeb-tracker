import math
from enum import Enum
from tkinter import messagebox
import customtkinter as ctk
from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from utilities.InvariantHelper import require_not_none


UNKNOWN_DATE_PLACEHOLDER = "never"
PAGE_SIZE = 15

class SearchFilterType(Enum):
    """
    Represents different filters that can be applied to the fleet during a
    search. Each filter is associated with a lambda function taking as an
    argument a bus list and a string, where the string is used to filter the bus
    list based on whether it is contained in the string representation of the
    selected attribute.
    For example, when TRACKING_NUM is selected with filter "2", all buses
    whose tracking number contains the digit "2" will be displayed.
    """
    TRACKING_NUM = "Tracking number"
    YEAR = "Year"
    MODEL = "Model"

FILTER_ACTIONS = {
    SearchFilterType.TRACKING_NUM: lambda bus_list, search_filter: [b for b in bus_list if search_filter in str(b.tracking_num)],
    SearchFilterType.YEAR: lambda bus_list, search_filter: [b for b in bus_list if search_filter in str(b.year)],
    SearchFilterType.MODEL: lambda bus_list, search_filter: [b for b in bus_list if search_filter in b.model]
}

INITIAL_FILTER = SearchFilterType.TRACKING_NUM

class ViewFleetFrame(ctk.CTkFrame, Listener):
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

        super().__init__(app)
        self.controller = controller
        self.fleet = fleet
        self.fleet.register_listener(self)
        self.curr_bus_list = fleet.sorted_buses()
        self.curr_page = 1
        self.curr_search_filter = lambda bus_list: bus_list

        # Header
        ctk.CTkLabel(self,
                     text="Fleet",
                     font=("Arial", 20, "bold")
                     ).pack()

        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(anchor="w", padx=10, pady=5)

        # Search filter entry
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...", width=250)
        self.search_entry.grid(row=0, column=0, sticky="w")

        # Submit search button
        search_button = ctk.CTkButton(search_frame, text="🔎", width=20, command=self.submit_search)
        search_button.grid(row=0, column=1, sticky="w", padx=5)

        # Dropdown menu of filter types for the search
        self.search_filter_menu = ctk.CTkOptionMenu(search_frame, values=[f.value for f in SearchFilterType])
        self.search_filter_menu.grid(row=0, column=2, sticky="w", padx=5)

        # Button to reset search (remove any filter that was applied)
        search_reset_button = ctk.CTkButton(search_frame, text="Reset", width=50, command=self.reset_search)
        search_reset_button.grid(row=0, column=3, sticky="w", padx=5)

        # Page information
        page_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        page_control_frame.pack(anchor="nw", padx=5)

        self.page_info = ctk.CTkLabel(page_control_frame, text=f"Page {self.curr_page} of {self._num_pages()}")
        self.page_info.pack(anchor="nw", padx=5)

        first_page_button = ctk.CTkButton(page_control_frame,
                                          text="<<", width=20, command=self._first_page)
        first_page_button.pack(anchor="nw", side="left", padx=2)
        prev_page_button = ctk.CTkButton(page_control_frame,
                                         text="<", width=20, command=self._prev_page)
        prev_page_button.pack(anchor="nw", side="left", padx=2)
        next_page_button = ctk.CTkButton(page_control_frame,
                                         text=">", width=20, command=self._next_page)
        next_page_button.pack(anchor="nw", side="left", padx=2)
        last_page_button = ctk.CTkButton(page_control_frame,
                                         text=">>", width=20, command=self._last_page)
        last_page_button.pack(anchor="nw", padx=2)

        # Initialize scrollable list
        self.bus_list = ctk.CTkScrollableFrame(self, width=900, height=650)
        self.bus_list.pack()

        self.notify()

    def reset_search(self) -> None:
        """
        Reconstructs the bus list with all filters removed and goes back
        to page 1.
        """
        self.curr_page = 1
        self.curr_search_filter = lambda bus_list: bus_list
        self.notify()

        self.search_entry.delete(0, "end")
        self.search_filter_menu.set(INITIAL_FILTER.value)

    def submit_search(self) -> None:
        """
        Filters the bus list based on the input provided in the search entry
        field and the search filter type menu. Takes no action if the search
        entry is empty or only whitespace. Does not validate input; invalid
        search filters will simply result in zero results.
        """
        search_filter: str = self.search_entry.get().strip()
        search_filter_type: SearchFilterType = SearchFilterType(self.search_filter_menu.get())

        self.curr_page = 1

        if len(search_filter) > 0:
            self.curr_search_filter = lambda bus_list: FILTER_ACTIONS[search_filter_type](bus_list, search_filter)
        self.notify()

    def confirm_remove_bus(self, bus: Bus) -> None:
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

    def _num_pages(self) -> int:
        """
        :return: the number of pages for the current number of buses to
        display (any search filters will be considered).
        """
        num_runs = len(self.curr_bus_list)

        if num_runs == 0:
            return 1

        return math.ceil(num_runs / PAGE_SIZE)

    def _next_page(self) -> None:
        """
        Increments the current page number if it does not exceed the total
        number of pages, then refreshes the bus list.
        """
        if self.curr_page + 1 <= self._num_pages():
            self.curr_page += 1
            self.notify()
            self.bus_list._parent_canvas.yview_moveto(0)

    def _prev_page(self) -> None:
        """
        Decrements the current page number if it is greater than 1, then
        refreshes the bus list.
        """
        if self.curr_page > 1:
            self.curr_page -= 1
            self.notify()
            self.bus_list._parent_canvas.yview_moveto(0)

    def _first_page(self) -> None:
        """
        Sets the current page number to 1, then refreshes the bus list.
        """
        self.curr_page = 1
        self.notify()
        self.bus_list._parent_canvas.yview_moveto(0)

    def _last_page(self) -> None:
        """
        Sets the current page number to the last page, then refreshes the
        bus list.
        """
        self.curr_page = self._num_pages()
        self.notify()
        self.bus_list._parent_canvas.yview_moveto(0)

    def notify(self) -> None:
        """
        Refreshes the list of buses and the page information in response to a
        change in the state of the fleet. Clears the old scrollable list of
        buses and reconstructs it, applying the current search filter and
        appending all necessary labels and buttons.
        """

        # Clear the old list
        for child in self.bus_list.winfo_children():
            child.destroy()

        # Apply the search filter to the bus list
        all_buses = self.fleet.sorted_buses()
        self.curr_bus_list = self.curr_search_filter(all_buses)

        # Update page info
        self.page_info.configure(text=f"Page {self.curr_page} of {self._num_pages()}")

        # Create the new list
        start_bus_index = (self.curr_page - 1) * PAGE_SIZE
        end_bus_index = start_bus_index + PAGE_SIZE

        for bus in self.curr_bus_list[start_bus_index:end_bus_index]:
            curr_row = ctk.CTkFrame(self.bus_list)
            curr_row.pack(fill="x", padx=5, pady=5)

            # Bus info
            tracking_num_label = ctk.CTkLabel(curr_row, text=f"{bus.tracking_num}", font=("Arial", 15, "bold"))
            tracking_num_label.pack(side="left", padx=5)

            model_label = ctk.CTkLabel(curr_row, text=f" {bus.year} {bus.model}")
            model_label.pack(side="left", padx=5)

            runs_label = ctk.CTkLabel(curr_row, text=f"{bus.num_runs()} runs ({self.fleet.percent_of_runs(bus)} %)")
            runs_label.pack(side="left", padx=5)

            last_seen_label = ctk.CTkLabel(curr_row, text=f"Last seen: {last_run_date_to_str(bus)}")
            last_seen_label.pack(side="left", padx=5)

            # "Remove" button
            (ctk.CTkButton(curr_row,
                           text="Remove",
                           height=20,
                           width=60,
                           command=lambda b=bus: self.confirm_remove_bus(b))
             .pack(side="right", padx=5))

        if len(self.curr_bus_list) == 0:
            no_results_label = ctk.CTkLabel(self.bus_list, text="No buses to display.")
            no_results_label.pack(anchor="nw")

def last_run_date_to_str(bus: Bus) -> str:
    """
    :bus: the bus for which to get the last run date as a string.
    :return: the last run completed by the given bus as a string of the form
    MONTH DAY, YEAR (e.g. May 2, 2026) or "never" if the given bus hasn't
    completed any runs.
    """
    if bus.last_run() is None:
        return UNKNOWN_DATE_PLACEHOLDER
    d = bus.last_run().run_date
    return f"{d.strftime('%B')} {d.day}, {d.year}"


