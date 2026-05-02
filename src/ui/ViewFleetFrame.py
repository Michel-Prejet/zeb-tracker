import customtkinter as ctk

from domain.Fleet import Fleet
from domain.Listener import Listener
from utilities.InvariantHelper import require_not_none


class ViewFleetFrame(ctk.CTkFrame, Listener):
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

    def notify(self):
        # Clear the old list
        for child in self.bus_list.winfo_children():
            child.destroy()

        # Create the new list
        for bus in self.fleet.sorted_buses():
            curr_row = ctk.CTkFrame(self.bus_list)
            curr_row.pack(fill="x", padx=5, pady=5)

            # Bus info
            (ctk.CTkLabel(curr_row, text=f"{bus.tracking_num}", font=("Arial", 15, "bold"))
             .pack(side="left", padx=5))
            ctk.CTkLabel(curr_row, text=f" {bus.year} {bus.model}").pack(side="left", padx=5)

            # "Remove" button
            (ctk.CTkButton(curr_row,
                          text="Remove",
                          height=20,
                          width=60,
                          command=lambda b=bus: self.controller.remove_bus(b))
             .pack(side="left", padx=5))


