from tkinter import messagebox
import customtkinter as ctk
from domain.Bus import Bus
from domain.Fleet import Fleet
from domain.Listener import Listener
from domain.Run import Run
from logic.RunFiltering.RunFilterType import RunFilterType
from logic.RunFiltering.RunFilterer import build_search_filter_function
from ui.pagination.Paginatable import Paginatable
from ui.pagination.PaginationFrame import PaginationFrame
from ui.runs.RunSearchFrame import RunSearchFrame
from ui.UIConstants import LARGE_TITLE_FONT, PADDING_LARGE, PADDING_MEDIUM, APP_WIDTH, SMALL_TITLE_FONT, \
    WIDE_ROW_BUTTON_WIDTH, WIDE_ROW_BUTTON_HEIGHT
from utilities.DateTimeHelper import format_date
from utilities.InvariantHelper import require_not_none


RUNS_PER_PAGE = 20

SCROLLABLE_LIST_DIMENSIONS = (APP_WIDTH, 650)
SCROLLABLE_LIST_WIDTH, SCROLLABLE_LIST_HEIGHT = SCROLLABLE_LIST_DIMENSIONS

class ViewRunsFrame(ctk.CTkFrame, Listener, Paginatable):
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
        require_not_none(fleet, "Fleet should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)

        self.app = app
        self.fleet = fleet
        self.controller = controller
        fleet.register_listener(self)

        self.runs = fleet.sorted_runs()
        self.curr_search_filter = lambda run_list: run_list
        self.curr_page = 1

        self._create_header()
        self._create_search_area()
        self._create_pagination_area()
        self._initialize_scrollable_list()

        self.notify()

    def notify(self) -> None:
        """
        Refreshes the list of runs and the page information in response to a
        change in the state of the buses within the fleet. Clears the old
        scrollable list of runs and reconstructs it, applying the current search
        filter and appending all necessary labels and buttons.
        """
        self._clear_scrollable_list()

        self._apply_search_filter()

        self.pagination_frame.update_page_info(self.curr_page)

        self._show_no_runs_in_list_if_empty()

        self._create_run_list()

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
            text="Runs",
            font=LARGE_TITLE_FONT
        ).pack()

    def _create_search_area(self) -> None:
        self.search_frame = RunSearchFrame(
            self,
            self._submit_search,
            self._reset_search
        )
        self.search_frame.pack(
            anchor="w",
            padx=PADDING_MEDIUM,
            pady=PADDING_MEDIUM
        )

    def _create_pagination_area(self) -> None:
        self.pagination_frame = PaginationFrame(
            parent=self,
            item_name="runs",
            items_per_page=RUNS_PER_PAGE,
            get_num_items=lambda: len(self.runs)
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
        all_runs = self.fleet.sorted_runs()
        self.runs = self.curr_search_filter(all_runs)

    def _show_no_runs_in_list_if_empty(self) -> None:
        if len(self.runs) == 0:
            ctk.CTkLabel(
                self.scrollable_list,
                text="No runs to display."
            ).pack(anchor="nw")

    def _create_run_list(self) -> None:
        start_run_index = (self.curr_page - 1) * RUNS_PER_PAGE
        end_run_index = start_run_index + RUNS_PER_PAGE

        for entry in self.runs[start_run_index:end_run_index]:
            run, bus = entry

            row = ctk.CTkFrame(self.scrollable_list)
            row.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)

            self._add_row_data(
                text=f"{format_date(run.run_date)}",
                row=row
            )

            self._add_row_data(
                text=f"Block {run.block_id}",
                row=row,
                font=SMALL_TITLE_FONT
            )

            self._add_row_data(
                text=f"🚍 {bus.tracking_num}",
                row=row
            )

            self._add_remove_button_to_row(entry, row)

    def _add_row_data(self, text: str, row: ctk.CTkFrame,
                      font: ctk.CTkFont | tuple | None = None) -> None:
        ctk.CTkLabel(
            row,
            text=text,
            font=font or ctk.CTkFont()
        ).pack(anchor="nw", side="left", padx=PADDING_LARGE)

    def _add_remove_button_to_row(self, data: tuple[Run, Bus], row: ctk.CTkFrame) -> None:
        ctk.CTkButton(
            row,
            text="Remove",
            width=WIDE_ROW_BUTTON_WIDTH,
            height=WIDE_ROW_BUTTON_HEIGHT,
            command=lambda d=data: self._confirm_remove_run(d)
        ).pack(side="right", padx=PADDING_MEDIUM)

    def _confirm_remove_run(self, data: tuple[Run, Bus]) -> None:
        """
        Displays a pop-up window asking the user to confirm that they would
        like to remove a run for a bus in the fleet. Removes the run if the user
        selects Yes.

        :param data: a RUN, BUS tuple containing the run to remove and the bus
        to remove it from if the user selects Yes.
        """
        run, bus = data

        confirmed = messagebox.askyesno(
            title="Remove run",
            message=f"Are you sure you want to remove this run?\n"
                    f"{format_date(run.run_date)} | Block {run.block_id} | Bus {bus.tracking_num}"
        )

        if confirmed:
            self.controller.remove_run_from_bus(bus, run)

    def _reset_search(self) -> None:
        """
        Reconstructs the run list with all filters removed and goes back
        to page 1.
        """
        self.curr_page = 1
        self.curr_search_filter = lambda run_list: run_list
        self.notify()

        self.search_frame.clear_input_fields()
        self.search_frame.reset_search_filter_menu()

    def _submit_search(self) -> None:
        """
        Filters the run list based on the input provided in the search entry
        field(s) and the search filter type menu, and goes back to page 1. Takes
        no action if the search entry is empty or only whitespace. Does not
        validate input (except dates); invalid search filters will simply result
        in zero results. For the DATE filter, an error message is displayed if
        the dates provided are not in YYYY-MM-DD format.
        """
        self.search_frame.remove_error_message()

        search_filter_type = self.search_frame.get_search_filter_selection()

        if search_filter_type == RunFilterType.DATE:
            try:
                self._get_date_range_search_filter_from_input()

                self.search_frame.clear_input_fields()
                self.curr_page = 1
                self.notify()
            except ValueError:
                self.search_frame.show_error("Dates should be in YYYY-MM-DD format.")
        else:
            self._get_general_search_filter_from_input(search_filter_type)

            self.search_frame.clear_input_fields()
            self.curr_page = 1
            self.notify()

    def _get_date_range_search_filter_from_input(self) -> None:
        start_date = self.search_frame.get_date_from_main_input()
        end_date = self.search_frame.get_date_from_extra_input()

        self.curr_search_filter = build_search_filter_function((start_date, end_date), RunFilterType.DATE)

    def _get_general_search_filter_from_input(self, filter_type: RunFilterType) -> None:
        text_filter = self.search_frame.get_main_input_raw()

        self.curr_search_filter = build_search_filter_function(text_filter, filter_type)




