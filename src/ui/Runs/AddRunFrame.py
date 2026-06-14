from typing import Callable
import customtkinter as ctk
from datetime import date, timedelta
from domain.InferredRunList import InferredRunList
from domain.Run import Run
from domain.validation.ValidateBus import validate_tracking_number
from domain.validation.ValidateRun import validate_date, validate_block_id
from domain.validation.exceptions.BusError import DuplicateRunError, InvalidTrackingNumberError
from domain.validation.exceptions.FleetError import BusNotFoundError
from domain.validation.exceptions.RunError import InvalidRunDateError, InvalidBlockIDError
from ui.Runs.AutoAddRunsFrame import AutoAddRunsFrame
from ui.UIConstants import PADDING_MEDIUM, PADDING_LARGE, LARGE_TITLE_FONT, MEDIUM_BUTTON_WIDTH, MEDIUM_BUTTON_HEIGHT, \
    CHECKBOX_WIDTH, CHECKBOX_HEIGHT, CHECKBOX_BORDER_WIDTH
from utilities.InvariantHelper import require_not_none


LABEL_COL = 0
INPUT_FIELD_COL = 1
TODAY_AUTOFILL_BUTTON_COL = 2
YESTERDAY_AUTOFILL_BUTTON_COL = 3
CHECKBOX_COL = 4

ERR_MESSAGES = {
    InvalidTrackingNumberError: "Tracking number should contain exactly three digits.",
    BusNotFoundError: "No bus exists with that tracking number.",
    InvalidRunDateError: "Date should be of the form YYYY-MM-DD.",
    InvalidBlockIDError: "Block ID should contain exactly one dash surrounded by digits.",
    DuplicateRunError: "Run already exists."
}

class AddRunFrame(ctk.CTkFrame):
    """
    Frame containing a form for adding a run to a bus in the fleet. Includes
    fields for the bus's tracking number, the date, and the block ID, along
    with a submit button. Displays error and success messages based on the
    validity of the input.
    """

    def __init__(self, app: ctk.CTk, inferred_runs: InferredRunList, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(inferred_runs, "Inferred run list should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)
        self.controller = controller

        self._configure_frame(inferred_runs, controller)
        self._create_header()
        self._create_input_fields_autofill_buttons_and_checkboxes()
        self._create_submit_area()

    def handle_enter(self, event=None) -> None:
        """
        Event handler for when the user presses the Enter key.
        """
        self._submit()

    def _submit(self) -> None:
        """
        Attempts to create a new bus based on the input provided in the fields.
        If successful, the run is added to the bus in the fleet, a success
        message is displayed, and the fields are cleared. Otherwise, an error
        message is displayed.
        """
        try:
            bus_tracking_num, runs = self._create_runs_from_input_fields()

            for run in runs:
                self.controller.add_run_to_bus(bus_tracking_num, run)
                self._show_success("Run added successfully.")

            self._clear_input_fields()
        except Exception as e:
            self._handle_error(e)

    def _configure_frame(self, inferred_runs: InferredRunList, controller) -> None:
        self.configure(fg_color="transparent")

        self.manual_adder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.manual_adder_frame.pack()

        self.auto_adder_frame = AutoAddRunsFrame(self, inferred_runs, controller)
        self.auto_adder_frame.pack(anchor="nw", padx=PADDING_LARGE)

    def _create_header(self) -> None:
        ctk.CTkLabel(
            self.manual_adder_frame,
            text="Add Run",
            font=LARGE_TITLE_FONT
        ).grid(row=0, column=INPUT_FIELD_COL, columnspan=2)

        ctk.CTkLabel(
            self.manual_adder_frame,
            text="Hold value"
        ).grid(row=1, column=CHECKBOX_COL, sticky="w")

    def _create_input_fields_autofill_buttons_and_checkboxes(self) -> None:
        self.bus_entry, self.bus_hold_value = self._add_labeled_input_field_with_hold_value_checkbox(
            label="Bus",
            placeholder="e.g. 971",
            row=2
        )

        self.date_entry, self.date_hold_value = self._add_labeled_input_field_with_hold_value_checkbox(
            label="Date (YYYY-MM-DD)",
            placeholder="e.g. 2025-12-01",
            row=3
        )
        self._create_date_autofill_button(
            label="Today",
            command=self._autofill_todays_date,
            col=TODAY_AUTOFILL_BUTTON_COL
        )

        self._create_date_autofill_button(
            label="Yesterday",
            command=self._autofill_yesterdays_date,
            col=YESTERDAY_AUTOFILL_BUTTON_COL
        )

        self.block_entry, self.block_id_hold_value = self._add_labeled_input_field_with_hold_value_checkbox(
            label="Block ID",
            placeholder="e.g. 8-22",
            row=4
        )

    def _add_labeled_input_field_with_hold_value_checkbox(
            self, label: str, placeholder: str, row: int) -> tuple[ctk.CTkEntry, ctk.CTkCheckBox]:
        ctk.CTkLabel(
            self.manual_adder_frame,
            text=label
        ).grid(row=row, column=LABEL_COL, padx=PADDING_LARGE, sticky="w")

        input_field = ctk.CTkEntry(
            self.manual_adder_frame,
            placeholder_text=placeholder
        )
        input_field.grid(row=row, column=INPUT_FIELD_COL, padx=PADDING_LARGE, sticky="w")

        hold_value_checkbox = ctk.CTkCheckBox(
            self.manual_adder_frame,
            text="",
            checkbox_width=CHECKBOX_WIDTH,
            checkbox_height=CHECKBOX_HEIGHT,
            border_width=CHECKBOX_BORDER_WIDTH
        )
        hold_value_checkbox.grid(row=row, column=CHECKBOX_COL, padx=PADDING_MEDIUM)

        return input_field, hold_value_checkbox

    def _create_date_autofill_button(self, label: str, command: Callable, col: int) -> None:
        ctk.CTkButton(
            self.manual_adder_frame,
            text=label,
            height=MEDIUM_BUTTON_HEIGHT,
            width=MEDIUM_BUTTON_WIDTH,
            fg_color="transparent",
            command=command
        ).grid(row=3, column=col, padx=PADDING_MEDIUM, sticky="w")

    def _autofill_todays_date(self) -> None:
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

    def _autofill_yesterdays_date(self) -> None:
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"))

    def _create_submit_area(self) -> None:
        ctk.CTkButton(
            self.manual_adder_frame,
            text="Add",
            command=self._submit
        ).grid(row=5, column=INPUT_FIELD_COL, pady=PADDING_LARGE)

        self.msg = ctk.CTkLabel(self.manual_adder_frame, text="", padx=PADDING_LARGE)
        self.msg.grid(row=6, column=LABEL_COL, columnspan=2)

    def _create_runs_from_input_fields(self) -> tuple[int, list[Run]]:
        bus_input = validate_tracking_number(self.bus_entry.get())
        date_input = validate_date(self.date_entry.get())
        block_input_list = map(validate_block_id, self.block_entry.get().split(","))

        return bus_input, [Run(b, date_input) for b in block_input_list]

    def _handle_error(self, e: Exception) -> None:
        message = ERR_MESSAGES.get(type(e))

        if message is not None:
            self._show_error(message)
        else:
            print("Unexpected error: " + str(e))

    def _show_success(self, message: str) -> None:
        self.msg.configure(text=message, text_color="green")

    def _show_error(self, message: str) -> None:
        self.msg.configure(text=message, text_color="red")

    def _clear_input_fields(self) -> None:
        if not self.bus_hold_value.get():
            self.bus_entry.delete(0, "end")
        if not self.date_hold_value.get():
            self.date_entry.delete(0, "end")
        if not self.block_id_hold_value.get():
            self.block_entry.delete(0, "end")