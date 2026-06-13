import math
from enum import Enum
from tkinter import messagebox
import customtkinter as ctk
from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from domain.Run import Run
from utilities.InvariantHelper import require_not_none
from datetime import date


PAGE_SIZE = 20

class SearchFilterType(Enum):
    """
    Represents different filters that can be applied to the list of runs during
    a search. Each filter is associated with a lambda function taking as an
    argument a list of (Run, Bus) tuples and a string, where the string is used
    to filter the run list based on whether it is contained in the string
    representation of the selected attribute (except for block IDs, which
    require an exact match).
    For example, when DATE is selected with filter "2026-05", all runs in
    May 2026 will be displayed.
    """
    DATE = "Date"
    BLOCK_ID = "Block ID"
    BUS_TRACKING_NUM = "Bus"
    BUS_MODEL = "Model"

FILTER_ACTIONS = {
    SearchFilterType.DATE: lambda run_list, start_date, end_date: [r for r in run_list if start_date <= r[0].run_date <= end_date],
    SearchFilterType.BLOCK_ID: lambda run_list, search_filter: [r for r in run_list if search_filter == r[0].block_id],
    SearchFilterType.BUS_TRACKING_NUM: lambda run_list, search_filter: [r for r in run_list if search_filter in str(r[1].tracking_num)],
    SearchFilterType.BUS_MODEL: lambda run_list, search_filter: [r for r in run_list if search_filter in r[1].model]
}

INITIAL_FILTER = SearchFilterType.DATE

class ViewRunsFrame(ctk.CTkFrame, Listener):
    """
    Frame displaying the list of runs in a given fleet, including the run
    date, the block ID, and the tracking number of the bus that completed the
    run. A search function and page information are displayed above the scrollable
    list. The search function includes an input field in which the user can enter
    a filter string, as well as a dropdown menu to select a filter and a button
    to submit the search. The page information section shows the current
    page, the total number of pages, and buttons to navigate to the next,
    previous, first, or last pages.
    """

    def __init__(self, app: ctk.CTk, fleet: Fleet, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)
        self.controller = controller
        self.fleet = fleet
        fleet.register_listener(self)
        self.curr_run_list = fleet.sorted_runs()
        self.curr_page = 1
        self.curr_search_filter = lambda run_list: run_list

        # Header
        ctk.CTkLabel(self,
                     text="Runs",
                     font=("Arial", 20, "bold")
                     ).pack()

        # Search frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(anchor="w", padx=10, pady=5)

        self.search_inputs_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_inputs_frame.grid(row=0, column=0, sticky="w")

        # Search field(s)
        self.search_entry_1 = ctk.CTkEntry(self.search_inputs_frame)
        self.search_entry_2 = ctk.CTkEntry(self.search_inputs_frame)

        # Submit search button
        search_button = ctk.CTkButton(self.search_frame, text="🔎", width=20, command=self.submit_search)
        search_button.grid(row=0, column=1, sticky="w", padx=5)

        # Dropdown menu of filter types for the search
        self.search_filter_menu = ctk.CTkOptionMenu(self.search_frame,
                                                    values=[f.value for f in SearchFilterType],
                                                    command=lambda _: self.refresh_search_inputs_frame())
        self.search_filter_menu.grid(row=0, column=2, sticky="w", padx=5)

        # Button to reset search
        search_reset_button = ctk.CTkButton(self.search_frame, text="Reset", width=50, command=self.reset_search)
        search_reset_button.grid(row=0, column=3, sticky="w", padx=5)

        # Error message for search filters
        self.search_err_msg = ctk.CTkLabel(self.search_frame, text="")

        # Page information
        page_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        page_control_frame.pack(anchor="nw", padx=5)

        self.page_info = ctk.CTkLabel(page_control_frame, text=f"Page {self.curr_page} of {self._num_pages()} "
                                                               f"({len(self.curr_run_list)} runs)")
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
        self.run_list = ctk.CTkScrollableFrame(self, width=900, height=650)
        self.run_list.pack()

        self.refresh_search_inputs_frame()
        self.notify()

    def handle_enter(self, event=None) -> None:
        """
        Event handler for when the user presses the Enter key. Submits the
        current search filter.

        :param event: the Tkinter event to handle (None by default).
        """
        self.submit_search()

    def handle_left_arrow(self, event=None) -> None:
        """
        Event handler for when the user presses the left arrow key. Goes to
        the previous page.

        :param event: the Tkinter event to handle (None by default).
        """
        self._prev_page()

    def handle_right_arrow(self, event=None) -> None:
        """
        Event handler for when the user presses the right arrow key. Goes to
        the next page.

        :param event: the Tkinter event to handle (None by default).
        """
        self._next_page()

    def reset_search(self) -> None:
        """
        Reconstructs the run list with all filters removed and goes back
        to page 1.
        """
        self.curr_page = 1
        self.curr_search_filter = lambda run_list: run_list
        self.notify()

        self.search_entry_1.delete(0, "end")
        self.search_entry_2.delete(0, "end")
        self.search_filter_menu.set(INITIAL_FILTER.value)

    def submit_search(self) -> None:
        """
        Filters the run list based on the input provided in the search entry
        field(s) and the search filter type menu, and goes back to page 1. Takes
        no action if the search entry is empty or only whitespace. Does not
        validate input (except dates); invalid search filters will simply result
        in zero results. For the DATE filter, an error message is displayed if
        the dates provided are not in YYYY-MM-DD format.
        """
        search_filter_type: SearchFilterType = SearchFilterType(self.search_filter_menu.get())
        if search_filter_type == SearchFilterType.DATE:
            start_date_raw = self.search_entry_1.get().strip()
            end_date_raw = self.search_entry_2.get().strip()

            try:
                start_date = date.fromisoformat(start_date_raw)
                end_date = date.fromisoformat(end_date_raw)
                self.curr_search_filter = lambda run_list: FILTER_ACTIONS[search_filter_type](run_list, start_date, end_date)
                self.notify()

                self.search_err_msg.grid_forget()
                self.search_entry_1.delete(0, "end")
                self.search_entry_2.delete(0, "end")
            except ValueError:
                self.search_err_msg.configure(text="Dates should be in YYYY-MM-DD format.", text_color="red")
                self.search_err_msg.grid(row=1, columnspan=3, sticky="w")
        else:
            search_filter = self.search_entry_1.get().strip()

            if len(search_filter) > 0:
                self.curr_search_filter = lambda run_list: FILTER_ACTIONS[search_filter_type](run_list, search_filter)
            self.notify()

            self.search_entry_1.delete(0, "end")

        self.curr_page = 1

    def refresh_search_inputs_frame(self) -> None:
        """
        Updates and resets the search input fields based on the current
        search filter type. If DATE is selected, two input fields are provided
        for start and end dates. Otherwise, a single input field is provided
        for the search filter.
        """
        self.search_entry_1.delete(0, "end")
        self.search_entry_2.delete(0, "end")
        self.search_err_msg.grid_forget()
        self.search_inputs_frame.focus_set()

        if self.search_filter_menu.get() == SearchFilterType.DATE.value:
            self.search_entry_1.configure(placeholder_text="Start date", width=125)
            self.search_entry_2.configure(placeholder_text="End date", width=125)
            self.search_entry_1.pack(anchor="w", side="left")
            self.search_entry_2.pack(anchor="w", padx=5)
        else:
            self.search_entry_2.pack_forget()
            self.search_entry_1.configure(placeholder_text="Search...", width=250)
            self.search_entry_1.pack(anchor="w")

    def confirm_remove_run(self, run: tuple[Run, Bus]) -> None:
        """
        Displays a pop-up window asking the user to confirm that they would
        like to remove a run for a bus in the fleet. Removes the run if the user
        selects Yes.

        :param run: a RUN, BUS tuple containing the run to remove and the bus
        to remove it from if the user selects Yes.
        """
        d = run[0].run_date
        run_date = f"{d.strftime('%B')} {d.day}, {d.year}"

        confirmed = messagebox.askyesno(
            "Remove run",
            f"Are you sure you want to remove this run?\n"
            f"{run_date} | Block {run[0].block_id} | Bus {run[1].tracking_num}"
        )

        if confirmed:
            self.controller.remove_run_from_bus(run[1], run[0])

    def _num_pages(self) -> int:
        """
        :return: the number of pages for the current number of runs to
        display (any search filters will be considered).
        """
        num_runs = len(self.curr_run_list)

        if num_runs == 0:
            return 1

        return math.ceil(num_runs / PAGE_SIZE)

    def _next_page(self) -> None:
        """
        Increments the current page number if it does not exceed the total
        number of pages, then refreshes the run list.
        """
        if self.curr_page + 1 <= self._num_pages():
            self.curr_page += 1
            self.notify()
            self.run_list._parent_canvas.yview_moveto(0)

    def _prev_page(self) -> None:
        """
        Decrements the current page number if it is greater than 1, then
        refreshes the run list.
        """
        if self.curr_page > 1:
            self.curr_page -= 1
            self.notify()
            self.run_list._parent_canvas.yview_moveto(0)

    def _first_page(self) -> None:
        """
        Sets the current page number to 1, then refreshes the run list.
        """
        self.curr_page = 1
        self.notify()
        self.run_list._parent_canvas.yview_moveto(0)

    def _last_page(self) -> None:
        """
        Sets the current page number to the last page, then refreshes the
        run list.
        """
        self.curr_page = self._num_pages()
        self.notify()
        self.run_list._parent_canvas.yview_moveto(0)

    def notify(self) -> None:
        """
        Refreshes the list of runs and the page information in response to a
        change in the state of the buses within the fleet. Clears the old
        scrollable list of runs and reconstructs it, applying the current search
        filter and appending all necessary labels and buttons.
        """

        # Clear the old list
        for child in self.run_list.winfo_children():
            child.destroy()

        # Apply the search filter to the run list
        all_runs = self.fleet.sorted_runs()
        self.curr_run_list = self.curr_search_filter(all_runs)

        # Update page info
        self.page_info.configure(text=f"Page {self.curr_page} of {self._num_pages()} "
                                      f"({len(self.curr_run_list)} runs)")

        # Create the new list
        start_run_index = (self.curr_page - 1) * PAGE_SIZE
        end_run_index = start_run_index + PAGE_SIZE

        for run in self.curr_run_list[start_run_index:end_run_index]:
            curr_row = ctk.CTkFrame(self.run_list)
            curr_row.pack(fill="x", padx=5, pady=5)

            # Run date
            d = run[0].run_date
            run_date = f"{d.strftime('%B')} {d.day}, {d.year}"
            ctk.CTkLabel(curr_row, text=run_date).pack(anchor="nw", side="left", padx=10)

            # Block ID
            (ctk.CTkLabel(curr_row, text=f"Block {run[0].block_id}", font=("Arial", 15, "bold"))
             .pack(anchor="nw", side="left", padx=10))

            # Bus
            (ctk.CTkLabel(curr_row, text=f"🚍 {run[1].tracking_num}")
             .pack(anchor="nw", side="left", padx=10))

            # Remove button
            (ctk.CTkButton(curr_row,
                           text="Remove",
                           height=20,
                           width=60,
                           command=lambda r=run: self.confirm_remove_run(r))
             .pack(side="right", padx=5))

        if len(self.curr_run_list) == 0:
            no_results_label = ctk.CTkLabel(self.run_list, text="No runs to display.")
            no_results_label.pack(anchor="nw")
