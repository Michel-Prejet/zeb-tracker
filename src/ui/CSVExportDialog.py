import customtkinter as ctk
from domain.Fleet import Fleet
from utilities.InvariantHelper import require_not_none
from utilities.csv_io.CSVExporter import create_csv_from_fleet


class CSVExportDialog(ctk.CTkToplevel):
    """
    Dialog containing the CSV export function. Takes a file name in an input
    field and attempts to export all run data from the given fleet to a CSV
    file with that name.
    """

    def __init__(self, app: ctk.CTk, fleet: Fleet):
        require_not_none(app, "App should not be None.")
        require_not_none(fleet, "Fleet should not be None.")

        super().__init__(app)
        self.fleet = fleet

        self.title("Export to CSV")
        self.geometry("400x250")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.transient(app)

        # Header
        ctk.CTkLabel(self, text="Export run data to CSV", font=("Arial", 20, "bold")).pack()

        inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        inputs_frame.pack(anchor="nw", pady=10)

        # Output file name entry
        ctk.CTkLabel(inputs_frame, text="Output file name").grid(row=1, column=0, sticky="w", padx=5)
        self.output_file_name = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. runs.csv")
        self.output_file_name.grid(row=1, column=1, sticky="w", padx=5)

        # Submit button and error message
        ctk.CTkButton(self, text="Export", command=self.submit).pack()
        self.msg = ctk.CTkLabel(self, text="")
        self.msg.pack()

    def submit(self) -> None:
        """
        Attempts to create a CSV file with the name provided in the input field
        containing all run data for this fleet. Prints an error message if the
        file name is empty. Otherwise, a success message is displayed.
        """
        try:
            file_name_input = self.output_file_name.get().strip()

            if len(file_name_input) == 0:
                raise EmptyFileNameError()
            elif not file_name_input.endswith(".csv"):
                file_name_input = file_name_input + ".csv"

            create_csv_from_fleet(file_name_input, self.fleet)

            self.msg.configure(text=f"Run data successfully exported to {file_name_input}.",
                               text_color="green")
            self.output_file_name.delete(0, "end")
        except EmptyFileNameError:
            self.msg.configure(text="File name cannot be empty.", text_color="red")
        except Exception as e:
            print("Unexpected error: " + str(e))

class EmptyFileNameError(Exception):
    """
    Exception thrown when a file name is left empty or blank in an input field.
    """
    pass