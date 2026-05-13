import math
from typing import Callable
import customtkinter as ctk
from domain.Fleet import Fleet
from domain.Listener import Listener
from domain.Run import Run
from utilities.InvariantHelper import require_not_none


class ViewRunsFrame(ctk.CTkFrame, Listener):
    PAGE_SIZE = 20

    def __init__(self, app: ctk.CTk, fleet: Fleet, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)
        self.controller = controller
        self.fleet = fleet
        self.fleet.register_listener(self)
        self.curr_page = 1

        # Header
        ctk.CTkLabel(self,
                     text="Runs",
                     font=("Arial", 20, "bold")
                     ).pack()

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
        self.run_list = ctk.CTkScrollableFrame(self, width=800, height=400)
        self.run_list.pack()

        self.notify()

    def _num_pages(self) -> int:
        """
        :return: the number of pages needed to display every run in the fleet
        (minimum of 1 page).
        """
        num_runs = len(self.fleet.sorted_runs())

        if num_runs == 0:
            return 1

        return math.ceil(num_runs / self.PAGE_SIZE)

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
        # Update page info
        self.page_info.configure(text=f"Page {self.curr_page} of {self._num_pages()}")

        # Clear the old list
        for child in self.run_list.winfo_children():
            child.destroy()

        # Create the new list
        start_run_index = (self.curr_page - 1) * self.PAGE_SIZE
        end_run_index = start_run_index + self.PAGE_SIZE

        for run in self.fleet.sorted_runs()[start_run_index:end_run_index]:
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
                           command=lambda r=run: self.controller.remove_run_from_bus(r[1], r[0]))
             .pack(side="right", padx=5))

