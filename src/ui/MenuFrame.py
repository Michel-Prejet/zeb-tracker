import customtkinter as ctk
from utilities.InvariantHelper import require_not_none


class MenuFrame(ctk.CTkFrame):
    """
    Frame displaying the menu for the application, which consists of a row
    of buttons allowing the user to navigate between frames.
    """

    def __init__(self, app: ctk.CTk, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)
        self.controller = controller

        self.configure(fg_color="transparent")

        self.view_fleet_button = ctk.CTkButton(self, text="View fleet", command=controller.switch_to_view_fleet_frame)
        self.view_fleet_button.pack(anchor="nw", side="left", padx=5, pady=10)

        self.view_runs_button = ctk.CTkButton(self, text="View runs", command=controller.switch_to_view_runs_frame)
        self.view_runs_button.pack(anchor="nw", side="left", padx=5, pady=10)

        self.add_bus_button = ctk.CTkButton(self, text="Add bus", command=controller.switch_to_add_bus_frame)
        self.add_bus_button.pack(anchor="nw", side="left", padx=5, pady=10)

        self.add_run_button = ctk.CTkButton(self, text="Add run", command=controller.switch_to_add_run_frame)
        self.add_run_button.pack(anchor="nw", side="left", padx=5, pady=10)

        self.csv_export_dialog = ctk.CTkButton(self, text="Export to CSV", command=controller.show_csv_export_dialog)
        self.csv_export_dialog.pack(anchor="nw", side="left", padx=5, pady=10)
