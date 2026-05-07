import customtkinter as ctk

from domain.Fleet import Fleet
from domain.validation.ValidateBus import *
from domain.validation.exceptions.FleetError import DuplicateBusError


class AddBusFrame(ctk.CTkFrame):
    """
    Frame containing a form for adding buses to the fleet. Includes
    fields for the tracking number, the model, and the year, along with a submit
    button. Displays error and success messages based on the validity of the
    input.
    """

    def __init__(self, app: ctk.CTk, fleet: Fleet, controller):
        require_not_none(app, "App should not be None.")
        require_not_none(fleet, "Fleet should not be None.")

        super().__init__(app)
        self.controller = controller

        self.configure(fg_color="transparent")

        # Header
        ctk.CTkLabel(self,
                            text="Add Bus",
                            font=("Arial", 20, "bold")
                     ).grid(row=0, column=0, columnspan=2)

        # Tracking number
        ctk.CTkLabel(self, text="Tracking number").grid(row=1, column=0, padx=10, sticky="w")
        self.tracking_num_entry = ctk.CTkEntry(self, placeholder_text="e.g. 971")
        self.tracking_num_entry.grid(row=1, column=1, padx=10)

        # Model
        ctk.CTkLabel(self, text="Model").grid(row=2, column=0, padx=10, sticky="w")
        self.model_entry = ctk.CTkEntry(self, placeholder_text="e.g. XE40")
        self.model_entry.grid(row=2, column=1, padx=10)

        # Year
        ctk.CTkLabel(self, text="Year").grid(row=3, column=0, padx=10, sticky="w")
        self.year_entry = ctk.CTkEntry(self, placeholder_text="e.g. 2025")
        self.year_entry.grid(row=3, column=1, padx=10)

        # Submit button and error message
        submit_button = ctk.CTkButton(self, text="Add", command=self.submit)
        submit_button.grid(row=4, column=1, pady=10)
        self.msg = ctk.CTkLabel(self, text="", padx=10)
        self.msg.grid(row=5, column=0, columnspan=2)

    def submit(self) -> None:
        """"
        Attempts to create a new bus based on the input provided in the fields.
        If successful, the bus is added to the fleet, a success message is
        displayed and the fields are cleared. Otherwise, an error message is
        displayed.
        """
        try:
            tracking_num_input = validate_tracking_number(self.tracking_num_entry.get())
            model_input = validate_model(self.model_entry.get())
            year_input = validate_year(self.year_entry.get())

            self.controller.add_bus(Bus(tracking_num_input, year_input, model_input))
            self.msg.configure(text="Bus added successfully.", text_color="green")

            self.tracking_num_entry.delete(0, "end")
            self.model_entry.delete(0, "end")
            self.year_entry.delete(0, "end")
        except InvalidTrackingNumberError:
            self.msg.configure(text="Tracking number should contain exactly three digits.", text_color="red")
        except InvalidYearError:
            self.msg.configure(text="Year should be an integer greater than or equal to 2000.", text_color="red")
        except EmptyModelError:
            self.msg.configure(text="Model should contain at least one character.", text_color="red")
        except DuplicateBusError:
            self.msg.configure(text="A bus already exists with that tracking number.", text_color="red")
        except Exception as e:
            print("Unexpected error: " + str(e))



