from datetime import date
from typing import Callable
import customtkinter as ctk
from domain.InferredRunList import InferredRunList
from domain.Listener import Listener
from ui.Pagination.Paginatable import Paginatable
from ui.Pagination.PaginationFrame import PaginationFrame
from ui.UIConstants import PADDING_MEDIUM, PADDING_LARGE, LARGE_TITLE_FONT, \
    FLAT_BUTTON_WIDTH, FLAT_BUTTON_HEIGHT, ROW_BUTTON_WIDTH, WIDE_ROW_BUTTON_WIDTH, ROW_BUTTON_HEIGHT, \
    WIDE_ROW_BUTTON_HEIGHT, APP_WIDTH
from utilities.InvariantHelper import require_not_none


RUNS_PER_PAGE = 10

BLOCK_ID_FONT = ("Arial", 15, "bold")

SCROLLABLE_LIST_DIMENSIONS = (APP_WIDTH, 275)
SCROLLABLE_LIST_WIDTH, SCROLLABLE_LIST_HEIGHT = SCROLLABLE_LIST_DIMENSIONS

class AutoAddRunsFrame(ctk.CTkFrame, Listener, Paginatable):
    """
    Frame containing a scrollable, paginated list of runs inferred from location
    data that the user can choose to add to the system. Each row contains the
    run's date, block ID, and bus tracking number, as well as buttons to add
    the run to the system or remove it from the list. Also includes an "Add
    all" button to add every run in the list.
    """

    def __init__(self, parent: ctk.CTkFrame, runs: InferredRunList, controller):
        require_not_none(parent, "Parent frame should not be None.")
        require_not_none(runs, "Inferred run list should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(parent)

        self.runs = runs
        self.controller = controller
        self.curr_page = 1

        self.runs.register_listener(self)

        self._configure_frame()
        self._create_header()
        self._create_pagination_area()
        self._create_add_all_button()
        self._create_scrollable_list()

    def notify(self) -> None:
        """
        Displays the current run data in the scrollable list with buttons to
        add runs to the fleet or remove them from the list, as well as a
        button to add all runs shown in the list. The scrollable list is
        cleared before displaying the new run data.
        """
        self._clear_scrollable_list_and_reset_add_all()

        self._update_page_info()

        self._show_no_runs_in_list_if_empty()

        self.add_all_runs_button.configure(
            command=self.controller.add_all_inferred_runs
        )

        self._create_run_list()

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
        self.run_list._parent_canvas.yview_moveto(0)

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _create_header(self) -> None:
        ctk.CTkLabel(
            self,
            text="Runs from Location Info",
            font=LARGE_TITLE_FONT
        ).pack(anchor="nw")

    def _create_pagination_area(self) -> None:
        self.pagination_frame = PaginationFrame(
            parent=self,
            item_name="runs",
            items_per_page=RUNS_PER_PAGE,
            get_num_items=lambda: len(self.runs)
        )
        self.pagination_frame.pack(anchor="nw", padx=PADDING_MEDIUM)

    def _update_page_info(self) -> None:
        if self.curr_page > self.pagination_frame.num_pages():
            self.curr_page = self.pagination_frame.num_pages()

        self.pagination_frame.update_page_info(self.curr_page)

    def _create_add_all_button(self) -> None:
        self.add_all_runs_button = ctk.CTkButton(
            self,
            text="Add all",
            width=FLAT_BUTTON_WIDTH,
            height=FLAT_BUTTON_HEIGHT
        )
        self.add_all_runs_button.pack(anchor="ne")

    def _create_scrollable_list(self) -> None:
        self.scrollable_list = ctk.CTkScrollableFrame(
            self,
            width=SCROLLABLE_LIST_WIDTH,
            height=SCROLLABLE_LIST_HEIGHT,
            fg_color="transparent"
        )
        self.scrollable_list.pack(anchor="nw")

        self._show_no_runs_in_list_if_empty()

    def _clear_scrollable_list_and_reset_add_all(self) -> None:
        for child in self.scrollable_list.winfo_children():
            child.destroy()

        self.add_all_runs_button.configure(command=None)

    def _show_no_runs_in_list_if_empty(self) -> None:
        if len(self.runs) == 0:
            ctk.CTkLabel(
                self.scrollable_list,
                text="No runs to display. Try running location fetch."
            ).pack(anchor="nw")

    def _create_run_list(self) -> None:
        start_run_index = (self.curr_page - 1) * RUNS_PER_PAGE
        end_run_index = start_run_index + RUNS_PER_PAGE

        for tracking_num in self.runs[start_run_index:end_run_index]:
            run = self.runs.get(tracking_num)

            row = ctk.CTkFrame(self.scrollable_list)
            row.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)

            self._add_row_data(
                text=_format_run_date(run.run_date), # Run date
                row=row
            )
            self._add_row_data(
                text=f"Block {run.block_id}", # Block ID
                row=row,
                font=BLOCK_ID_FONT
            )
            self._add_row_data(
                text=f"🚍 {tracking_num}", # Bus tracking number
                row=row
            )

            self._add_row_button(
                label="Add",
                command=lambda b=tracking_num: self.controller.add_inferred_run_for_bus(b),
                width=ROW_BUTTON_WIDTH,
                height=ROW_BUTTON_HEIGHT,
                row=row
            )
            self._add_row_button(
                label="Remove",
                command=lambda b=tracking_num: self.runs.remove(b),
                width=WIDE_ROW_BUTTON_WIDTH,
                height=WIDE_ROW_BUTTON_HEIGHT,
                row=row
            )

    def _add_row_data(self, text: str, row: ctk.CTkFrame,
                      font: ctk.CTkFont | tuple | None = None) -> None:
        ctk.CTkLabel(
            row,
            text=text,
            font=font or ctk.CTkFont(),
        ).pack(anchor="nw", side="left", padx=PADDING_LARGE)

    def _add_row_button(self, label: str, command: Callable, width: int,
                        height: int, row: ctk.CTkFrame) -> None:
        ctk.CTkButton(
            row,
            text=label,
            height=height,
            width=width,
            command=command
        ).pack(side="right", padx=PADDING_MEDIUM)

def _format_run_date(run_date: date) -> str:
    return f"{run_date.strftime('%B')} {run_date.day}, {run_date.year}"