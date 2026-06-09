import math
from datetime import date
from typing import Callable
import customtkinter as ctk
from domain.InferredRunList import InferredRunList
from domain.Listener import Listener
from utilities.InvariantHelper import require_not_none


RUNS_PER_PAGE = 10

TITLE_FONT = ("Arial", 16, "bold")
BLOCK_ID_FONT = ("Arial", 15, "bold")

PADX_PAGE_CONTROL_FRAME = 5
PADX_PAGE_INFO_LABEL = 5
PADX_PAGE_BUTTON = 2
PADX_ROW_FRAME = 5
PADY_ROW_FRAME = 5
PADX_ROW_DATA = 10
PADX_ROW_BUTTON = 5

SCROLLABLE_LIST_WIDTH = 800
SCROLLABLE_LIST_HEIGHT = 275
ADD_ALL_BUTTON_WIDTH = 20
ADD_ALL_BUTTON_HEIGHT = 10
PAGE_BUTTON_WIDTH = 20
ROW_BUTTON_HEIGHT = 20
ROW_ADD_BUTTON_WIDTH = 30
ROW_REMOVE_BUTTON_WIDTH = 60

class AutoAddRunsFrame(ctk.CTkFrame, Listener):
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
        self._create_page_information_and_controls()
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
        self._prev_page()

    def handle_right_arrow(self, event=None) -> None:
        """
        Event handler for when the user presses the right arrow key.
        """
        self._next_page()

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _create_header(self) -> None:
        ctk.CTkLabel(
            self,
            text="Runs from Location Info",
            font=TITLE_FONT
        ).pack(anchor="nw")

    def _create_page_information_and_controls(self) -> None:
        self.page_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.page_control_frame.pack(anchor="nw", padx=PADX_PAGE_CONTROL_FRAME)

        self.page_info = ctk.CTkLabel(self.page_control_frame)
        self.page_info.pack(anchor="nw", padx=PADX_PAGE_INFO_LABEL)
        self._update_page_info()

        self._create_page_button("<<", self._first_page)
        self._create_page_button("<", self._prev_page)
        self._create_page_button(">", self._next_page)
        self._create_page_button(">>", self._last_page)

    def _update_page_info(self) -> None:
        if self.curr_page > self._num_pages():
            self.curr_page = self._num_pages()

        self.page_info.configure(
            text=f"Page {self.curr_page} of {self._num_pages()} ({len(self.runs)} runs)"
        )

    def _create_page_button(self, label: str, command: Callable) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self.page_control_frame,
            text=label,
            width=PAGE_BUTTON_WIDTH,
            command=command
        )
        button.pack(anchor="nw", side="left", padx=PADX_PAGE_BUTTON)

        return button

    def _num_pages(self) -> int:
        """
        :return: the number of pages for the current number of runs to
        display.
        """
        num_runs = len(self.runs)

        if num_runs == 0:
            return 1

        return math.ceil(num_runs / RUNS_PER_PAGE)

    def _next_page(self) -> None:
        if self.curr_page + 1 <= self._num_pages():
            self.curr_page += 1
            self._refresh_and_go_to_top_of_page()

    def _prev_page(self) -> None:
        if self.curr_page > 1:
            self.curr_page -= 1
            self._refresh_and_go_to_top_of_page()

    def _first_page(self) -> None:
        self.curr_page = 1
        self._refresh_and_go_to_top_of_page()

    def _last_page(self) -> None:
        self.curr_page = self._num_pages()
        self._refresh_and_go_to_top_of_page()

    def _refresh_and_go_to_top_of_page(self) -> None:
        self.notify()
        self.run_list._parent_canvas.yview_moveto(0)

    def _create_add_all_button(self) -> None:
        self.add_all_runs_button = ctk.CTkButton(
            self,
            text="Add all",
            width=ADD_ALL_BUTTON_WIDTH,
            height=ADD_ALL_BUTTON_HEIGHT
        )
        self.add_all_runs_button.pack(anchor="ne")

    def _create_scrollable_list(self) -> None:
        self.run_list = ctk.CTkScrollableFrame(
            self,
            width=SCROLLABLE_LIST_WIDTH,
            height=SCROLLABLE_LIST_HEIGHT,
            fg_color="transparent"
        )
        self.run_list.pack(anchor="nw")

        self._show_no_runs_in_list_if_empty()

    def _clear_scrollable_list_and_reset_add_all(self) -> None:
        for child in self.run_list.winfo_children():
            child.destroy()

        self.add_all_runs_button.configure(command=None)

    def _show_no_runs_in_list_if_empty(self) -> None:
        if len(self.runs) == 0:
            ctk.CTkLabel(
                self.run_list,
                text="No runs to display. Try running location fetch."
            ).pack(anchor="nw")

    def _create_run_list(self) -> None:
        start_run_index = (self.curr_page - 1) * RUNS_PER_PAGE
        end_run_index = start_run_index + RUNS_PER_PAGE

        for tracking_num in self.runs[start_run_index:end_run_index]:
            run = self.runs.get(tracking_num)

            row = ctk.CTkFrame(self.run_list)
            row.pack(fill="x", padx=PADX_ROW_FRAME, pady=PADY_ROW_FRAME)

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
                width=ROW_ADD_BUTTON_WIDTH,
                row=row
            )
            self._add_row_button(
                label="Remove",
                command=lambda b=tracking_num: self.runs.remove(b),
                width=ROW_REMOVE_BUTTON_WIDTH,
                row=row
            )

    def _add_row_data(self, text: str, row: ctk.CTkFrame,
                      font: ctk.CTkFont | tuple | None = None) -> None:
        ctk.CTkLabel(
            row,
            text=text,
            font=font or ctk.CTkFont(),
        ).pack(anchor="nw", side="left", padx=PADX_ROW_DATA)

    def _add_row_button(self, label: str, command: Callable, width: int, row: ctk.CTkFrame) -> None:
        ctk.CTkButton(
            row,
            text=label,
            height=ROW_BUTTON_HEIGHT,
            width=width,
            command=command
        ).pack(side="right", padx=PADX_ROW_BUTTON)

def _format_run_date(run_date: date) -> str:
    return f"{run_date.strftime('%B')} {run_date.day}, {run_date.year}"