from enum import Enum
from typing import Callable
import customtkinter as ctk
from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from utilities.InvariantHelper import require_not_none


UNKNOWN_DATE_PLACEHOLDER = "never"

class SearchFilterType(Enum):
    """
    Represents different filters that can be applied to the fleet during a
    search. Each filter (except for DEFAULT) is associated with a lambda
    function taking as arguments a bus list and a string, where the string
    is used to filter the bus list based on whether it is contained in the
    string representation of the selected attribute.
    For example, when TRACKING_NUM is selected with filter "2", all buses
    whose tracking number contains the digit "2" will be displayed.
    """
    DEFAULT = "Search by..."
    TRACKING_NUM = "Tracking number"
    YEAR = "Year"
    MODEL = "Model"

FILTER_ACTIONS = {
    SearchFilterType.TRACKING_NUM: lambda bus_list, search_filter: [b for b in bus_list if search_filter in str(b.tracking_num)],
    SearchFilterType.YEAR: lambda bus_list, search_filter: [b for b in bus_list if search_filter in str(b.year)],
    SearchFilterType.MODEL: lambda bus_list, search_filter: [b for b in bus_list if search_filter in b.model]
}

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

        # Initialize scrollable list
        self.bus_list = ctk.CTkScrollableFrame(self, width=800, height=400)
        self.bus_list.pack()

        self.notify()

    def submit_search(self) -> None:
        """
        Filters the bus list based on the input provided in the search entry
        field and the search filter type menu. Takes no action if the filter
        type is DEFAULT or the search entry is empty or only whitespace. Does
        not validate input; invalid search filters will simply result in zero
        results.
        """
        search_filter: str = self.search_entry.get().strip()
        search_filter_type: SearchFilterType = SearchFilterType(self.search_filter_menu.get())

        if search_filter_type != SearchFilterType.DEFAULT and len(search_filter) > 0:
            self._display_list(
                lambda buses: FILTER_ACTIONS[search_filter_type](buses, search_filter)
            )

    def reset_search(self) -> None:
        """
        Reconstructs the bus list with all filters removed.
        """
        self._display_list(lambda buses: buses)

        self.search_entry.delete(0, "end")
        self.search_filter_menu.set(SearchFilterType.DEFAULT.value)

    def notify(self) -> None:
        """
        Refreshes the list of buses in response to a change in the state of the
        fleet.
        """
        self._display_list(lambda buses: buses)

    def _display_list(self, bus_filterer: Callable) -> None:
        """
        Populates the scrollable list of buses in the fleet. The list is filtered
        using a given lambda function. Clears the old list and reconstructs it,
        appending all necessary labels and buttons.

        :param bus_filterer: the function by which to filter the bus list.
        """
        # Clear the old list
        for child in self.bus_list.winfo_children():
            child.destroy()

        # Create the new, filtered list
        list_to_display = bus_filterer(self.fleet.sorted_buses())
        for bus in list_to_display:
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
                           command=lambda b=bus: self.controller.remove_bus(b))
             .pack(side="right", padx=5))

        if len(list_to_display) == 0:
            no_results_label = ctk.CTkLabel(self.bus_list, text="No results.")
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


