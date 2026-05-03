import customtkinter as ctk

from domain.Fleet import Fleet
from domain.Listener import Listener
from utilities.InvariantHelper import require_not_none


class ViewFleetFrame(ctk.CTkFrame, Listener):
    """
    Frame displaying the list of buses in a given fleet, including their
    tracking number, model info, the date of their last run, and a "remove"
    button.
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
                     text="View Fleet",
                     font=("Arial", 20, "bold")
                     ).pack()

        # Initialize scrollable list
        self.bus_list = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.bus_list.pack()

        self.notify()

    def notify(self) -> None:
        """
        Refreshes the list of buses in response to a change in the state of the
        fleet. Clears the old list and reconstructs it, appending all necessary
        labels and buttons.
        """
        # Clear the old list
        for child in self.bus_list.winfo_children():
            child.destroy()

        # Create the new list
        for bus in self.fleet.sorted_buses():
            curr_row = ctk.CTkFrame(self.bus_list)
            curr_row.pack(fill="x", padx=5, pady=5)

            # Bus info
            tracking_num_label = ctk.CTkLabel(curr_row, text=f"{bus.tracking_num}", font=("Arial", 15, "bold"))
            tracking_num_label.pack(side="left", padx=5)

            model_label = ctk.CTkLabel(curr_row, text=f" {bus.year} {bus.model}")
            model_label.pack(side="left", padx=5)

            runs_label = ctk.CTkLabel(curr_row, text=f"{bus.num_runs()} runs ({self.fleet.percent_of_runs(bus)} %)")
            runs_label.pack(side="left", padx=5)

            last_seen_label = ctk.CTkLabel(curr_row, text=f"Last seen: {bus.last_run_as_str()}")
            last_seen_label.pack(side="left", padx=5)

            # "Remove" button
            (ctk.CTkButton(curr_row,
                          text="Remove",
                          height=20,
                          width=60,
                          command=lambda b=bus: self.controller.remove_bus(b))
             .pack(side="right", padx=5))


