from typing import Callable
import customtkinter as ctk
from ui.UIConstants import PADDING_MEDIUM, PADDING_LARGE
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

        self._configure_frame()
        self._create_buttons()

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _create_buttons(self) -> None:
        self._create_menu_button(
            label="View fleet",
            command=self.controller.switch_to_view_fleet_frame
        )

        self._create_menu_button(
            label="View runs",
            command=self.controller.switch_to_view_runs_frame
        )

        self._create_menu_button(
            label="Add bus",
            command=self.controller.switch_to_add_bus_frame
        )

        self._create_menu_button(
            label="Add run",
            command=self.controller.switch_to_add_run_frame
        )

        self._create_menu_button(
            label="Export to CSV",
            command=self.controller.show_csv_export_dialog
        )

    def _create_menu_button(self, label: str, command: Callable) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=label,
            command=command
        )
        button.pack(anchor="nw", side="left", padx=PADDING_MEDIUM, pady=PADDING_LARGE)

        return button
