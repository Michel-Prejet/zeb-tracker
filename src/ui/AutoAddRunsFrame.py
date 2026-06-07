import math
import customtkinter as ctk
from domain.InferredRunList import InferredRunList
from domain.Listener import Listener
from utilities.InvariantHelper import require_not_none


PAGE_SIZE = 10

class AutoAddRunsFrame(ctk.CTkFrame, Listener):
    def __init__(self, parent: ctk.CTkFrame, runs: InferredRunList, controller):
        require_not_none(parent, "Parent frame should not be None.")
        require_not_none(runs, "Inferred run list should not be None.")

        super().__init__(parent)
        self.runs = runs
        self.controller = controller
        self.curr_page = 1

        self.runs.register_listener(self)

        self.configure(fg_color="transparent")

        # Header
        ctk.CTkLabel(
            self,
            text="Runs from Location Info",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="nw")

        # Page information
        page_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        page_control_frame.pack(anchor="nw", padx=5)

        self.page_info = ctk.CTkLabel(
            page_control_frame,
            text=f"Page {self.curr_page} of {self._num_pages()} ({len(self.runs)} runs)",
        )
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
        last_page_button.pack(anchor="nw", padx=2, side="left")

        # Add all button
        self.add_all_runs_button = ctk.CTkButton(
            self,
            text="Add all",
            height=10,
            width=20
        )
        self.add_all_runs_button.pack(anchor="ne")

        # Scrollable list of runs
        self.run_list = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=275,
            fg_color="transparent"
        )
        self.run_list.pack(anchor="nw")
        self._show_no_runs_in_list()

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

    def notify(self) -> None:
        """
        Displays the current run data in the scrollable list with buttons to
        add runs to the fleet or remove them from the list, as well as a
        button to add all runs shown in the list. The scrollable list is
        cleared before displaying the new run data.
        """
        self._clear_scrollable_list_and_reset_add_all()

        # Update page info
        if self.curr_page > self._num_pages():
            self.curr_page = self._num_pages()
        self.page_info.configure(
            text=f"Page {self.curr_page} of {self._num_pages()} ({len(self.runs)} runs)"
        )

        if len(self.runs) == 0:
            self._show_no_runs_in_list()
            return

        # Create the new list
        start_run_index = (self.curr_page - 1) * PAGE_SIZE
        end_run_index = start_run_index + PAGE_SIZE

        self.add_all_runs_button.configure(
            command=self.controller.add_all_inferred_runs
        )

        for tracking_num in self.runs[start_run_index:end_run_index]:
            run = self.runs.get(tracking_num)

            row = ctk.CTkFrame(self.run_list)
            row.pack(fill="x", padx=5, pady=5)

            # Run date
            d = run.run_date
            ctk.CTkLabel(
                row,
                text=f"{d.strftime('%B')} {d.day}, {d.year}",
            ).pack(anchor="nw", side="left", padx=10)

            # Block ID
            ctk.CTkLabel(
                row,
                text=f"Block {run.block_id}",
                font=("Arial", 15, "bold")
            ).pack(anchor="nw", side="left", padx=10)

            # Bus
            ctk.CTkLabel(
                row,
                text=f"🚍 {tracking_num}"
            ).pack(anchor="nw", side="left", padx=10)

            # Add button
            ctk.CTkButton(
                row,
                text="Add",
                height=20,
                width=30,
                command=lambda b=tracking_num: self.controller.add_inferred_run_for_bus(b)
            ).pack(side="right", padx=5)

            # Remove button
            ctk.CTkButton(
                row,
                text="Remove",
                height=20,
                width=60,
                command=lambda b=tracking_num: self.runs.remove(b)
            ).pack(side="right", padx=5)

    def _show_no_runs_in_list(self) -> None:
        ctk.CTkLabel(
            self.run_list,
            text="No runs to display. Try running location fetch."
        ).pack(anchor="nw")

    def _clear_scrollable_list_and_reset_add_all(self) -> None:
        """
        Removes all rows in the scrollable list and clears the command
        associated with the Add all button.
        """
        for child in self.run_list.winfo_children():
            child.destroy()

        self.add_all_runs_button.configure(command=None)

    def _num_pages(self) -> int:
        """
        :return: the number of pages for the current number of runs to
        display.
        """
        num_runs = len(self.runs)

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