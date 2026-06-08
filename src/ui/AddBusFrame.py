import customtkinter as ctk
from domain.Bus import Bus
from domain.validation.ValidateBus import validate_tracking_number, validate_model, validate_year
from domain.validation.exceptions.BusError import InvalidTrackingNumberError, InvalidYearError, EmptyModelError
from domain.validation.exceptions.FleetError import DuplicateBusError
from utilities.InvariantHelper import require_not_none


PAD_X = 10
PAD_Y = 10
TITLE_FONT = ("Arial", 20, "bold")

LABEL_COL = 0
INPUT_FIELD_COL = 1

ERR_MESSAGES = {
    InvalidTrackingNumberError: "Tracking number should contain exactly three digits.",
    InvalidYearError: "Year should be an integer greater than or equal to 2000.",
    EmptyModelError: "Model should contain at least one character.",
    DuplicateBusError: "A bus already exists with that tracking number."
}

class AddBusFrame(ctk.CTkFrame):
    """
    Frame containing a form for adding buses to the fleet. Includes
    fields for the tracking number, the model, and the year, along with a submit
    button. Displays error and success messages based on the validity of the
    input.
    """

    def __init__(self, app: ctk.CTk, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)

        self.controller = controller

        self._configure_frame()
        self._create_header()
        self._create_input_fields()
        self._create_submit_area()

    def submit(self) -> None:
        """
        Attempts to create a new bus based on the input provided in the fields.
        If successful, the bus is added to the fleet, a success message is
        displayed and the fields are cleared. Otherwise, an error message is
        displayed.
        """
        try:
            bus = self._create_bus_from_input_fields()
            self.controller.add_bus(bus)

            self._show_success("Bus added successfully.")
            self._clear_input_fields()
        except Exception as e:
            self._handle_error(e)

    def handle_enter(self, event=None) -> None:
        """
        Event handler for when the user presses the Enter key. Submits the
        current input to create a new bus.

        :param event: the Tkinter event to handle (None by default).
        """
        self.submit()

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _create_header(self) -> None:
        ctk.CTkLabel(
            self,
            text="Add Bus",
            font=TITLE_FONT
        ).grid(row=0, column=LABEL_COL, columnspan=2)

    def _create_input_fields(self) -> None:
        self.tracking_num_entry = self._create_labelled_input_field(
            label="Tracking number",
            placeholder="e.g. 971",
            row=1
        )

        self.model_entry = self._create_labelled_input_field(
            label="Model",
            placeholder="e.g. XE40",
            row=2
        )

        self.year_entry = self._create_labelled_input_field(
            label="Year",
            placeholder="e.g. 2025",
            row=3
        )

    def _create_submit_area(self) -> None:
        submit_button = ctk.CTkButton(
            self,
            text="Add",
            command=self.submit
        )
        submit_button.grid(row=4, column=INPUT_FIELD_COL, pady=PAD_Y)

        self.msg = ctk.CTkLabel(self, text="", padx=PAD_X)
        self.msg.grid(row=5, column=LABEL_COL, columnspan=2)

    def _create_labelled_input_field(self, label: str, placeholder: str,
                                     row: int) -> ctk.CTkEntry:
        ctk.CTkLabel(
            self,
            text=label
        ).grid(row=row, column=LABEL_COL, padx=PAD_X, sticky="w")

        input_field = ctk.CTkEntry(self, placeholder_text=placeholder)
        input_field.grid(row=row, column=INPUT_FIELD_COL, padx=PAD_X)

        return input_field

    def _create_bus_from_input_fields(self) -> Bus:
        tracking_num_input = validate_tracking_number(self.tracking_num_entry.get())
        model_input = validate_model(self.model_entry.get())
        year_input = validate_year(self.year_entry.get())

        return Bus(tracking_num_input, year_input, model_input)

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
        self.tracking_num_entry.delete(0, "end")
        self.model_entry.delete(0, "end")
        self.year_entry.delete(0, "end")



