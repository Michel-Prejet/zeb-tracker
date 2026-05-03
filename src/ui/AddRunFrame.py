import customtkinter as ctk

from domain.Fleet import Fleet
from domain.Run import Run
from domain.validation.ValidateBus import validate_tracking_number
from domain.validation.ValidateRun import validate_date, validate_block_id
from domain.validation.exceptions.BusError import DuplicateRunError, InvalidTrackingNumberError
from domain.validation.exceptions.FleetError import BusNotFoundError
from domain.validation.exceptions.RunError import InvalidRunDateError, InvalidBlockIDError
from utilities.InvariantHelper import require_not_none

class AddRunFrame(ctk.CTkFrame):
    """
    Frame containing a form for adding a run to a bus in the fleet. Includes
    fields for the bus's tracking number, the date, and the block ID, along
    with a submit button. Displays error and success messages based on the
    validity of the input.
    """

    def __init__(self, app: ctk.CTk, fleet: Fleet, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)
        self.controller = controller
        self.fleet = fleet

        # Header
        ctk.CTkLabel(self,
                     text="Add Run",
                     font=("Arial", 20, "bold")
                     ).grid(row=0, column=0, columnspan=2)

        # Bus tracking number
        ctk.CTkLabel(self, text="Bus").grid(row=1, column=0, padx=10, sticky="w")
        self.bus_entry = ctk.CTkEntry(self, placeholder_text="e.g. 971")
        self.bus_entry.grid(row=1, column=1, padx=10, sticky="w")

        # Date
        ctk.CTkLabel(self, text="Date (YYYY-MM-DD)").grid(row=2, column=0, padx=10, sticky="w")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="e.g. 2025-12-01")
        self.date_entry.grid(row=2, column=1, padx=10, sticky="w")

        # Block ID
        ctk.CTkLabel(self, text="Block ID").grid(row=3, column=0, padx=10, sticky="w")
        self.block_entry = ctk.CTkEntry(self, placeholder_text="e.g. 8-22")
        self.block_entry.grid(row=3, column=1, padx=10, sticky="w")

        # Submit button and error message
        ctk.CTkButton(self, text="Add", command=self.submit).grid(row=4, column=1, pady=10)
        self.msg = ctk.CTkLabel(self, text="", padx=10)
        self.msg.grid(row=5, column=0, columnspan=2)

    def submit(self) -> None:
        """
        Attempts to create a new bus based on the input provided in the fields.
        If successful, the run is added to the bus in the fleet, a success
        message is displayed, and the fields are cleared. Otherwise, an error
        message is displayed.
        """
        try:
            bus_input = validate_tracking_number(self.bus_entry.get())
            bus = self.fleet.get_bus(bus_input)
            date_input = validate_date(self.date_entry.get())
            block_input = validate_block_id(self.block_entry.get())

            self.controller.add_run_to_bus(bus, Run(block_input, date_input))
            self.msg.configure(text="Run added successfully.", text_color="green")

            self.bus_entry.delete(0, "end")
            self.date_entry.delete(0, "end")
            self.block_entry.delete(0, "end")
        except InvalidTrackingNumberError:
            self.msg.configure(text="Tracking number should contain exactly three digits.", text_color="red")
        except BusNotFoundError:
            self.msg.configure(text="No bus exists with that tracking number.", text_color="red")
        except InvalidRunDateError:
            self.msg.configure(text="Date should be of the form YYYY-MM-DD.", text_color="red")
        except InvalidBlockIDError:
            self.msg.configure(text="Block ID should contain exactly one dash surrounded by digits.", text_color="red")
        except DuplicateRunError:
            self.msg.configure(text="Run already exists.", text_color="red")
        except Exception as e:
            print("Unexpected error: " + str(e))