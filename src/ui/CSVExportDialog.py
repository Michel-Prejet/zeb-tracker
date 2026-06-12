from datetime import date
from pathlib import Path
from tkinter import filedialog
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
        self.geometry("500x250")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.transient(app)

        # Header
        ctk.CTkLabel(self, text="Export run data to CSV", font=("Arial", 20, "bold")).pack()

        inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        inputs_frame.pack(anchor="nw", pady=10)

        # File path entry
        ctk.CTkLabel(inputs_frame, text="File path").grid(row=1, column=0, sticky="w", padx=5)
        self.folder_path_entry = ctk.CTkEntry(inputs_frame)
        self.folder_path_entry.grid(row=1, column=1, sticky="w", padx=5)
        browse_button = ctk.CTkButton(inputs_frame, text="📂", command=self.browse_for_folder_path, width=5)
        browse_button.grid(row=1, column=2, sticky="w", padx=5)

        # Output file name entry
        ctk.CTkLabel(inputs_frame, text="Output file name").grid(row=2, column=0, sticky="w", padx=5)
        self.output_file_name = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. runs.csv")
        self.output_file_name.grid(row=2, column=1, sticky="w", padx=5)

        # Start date entry
        ctk.CTkLabel(inputs_frame, text="Start date (optional)").grid(row=3, column=0, sticky="w", padx=5)
        self.start_date_entry = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. 2026-05-01")
        self.start_date_entry.grid(row=3, column=1, sticky="w", padx=5)

        # Submit button and error message
        ctk.CTkButton(self, text="Export", command=self.submit).pack()
        self.msg = ctk.CTkLabel(self, text="")
        self.msg.pack()

    def submit(self) -> None:
        """
        Attempts to create a CSV file containing all run data for this fleet with
        the folder path, name, and (optionally) the start date provided in the
        input fields. Prints an error message if the folder path or the file
        name are empty, if the folder path is invalid or doesn't exist, or if
        the start date is non-empty and not of the form YYYY-MM-DD. Otherwise,
        a success message is displayed.
        """
        try:
            fleet_to_export = self.fleet.sorted_runs()

            if not self.folder_path_entry.get().strip():
                raise InvalidFolderPathError()

            file_name_input = self.output_file_name.get().strip()
            if len(file_name_input) == 0:
                raise EmptyFileNameError()
            elif not file_name_input.endswith(".csv"):
                file_name_input = file_name_input + ".csv"

            try:
                file_path = Path(self.folder_path_entry.get() + "/" + file_name_input)
            except TypeError:
                raise InvalidFolderPathError()

            start_date_input = self.start_date_entry.get().strip()
            if len(start_date_input) > 0:
                start_date = date.fromisoformat(start_date_input)
                fleet_to_export = self.fleet.runs_starting_at_date(start_date)

            try:
                create_csv_from_fleet(str(file_path), fleet_to_export)
            except FileNotFoundError:
                raise InvalidFolderPathError()

            self.msg.configure(text=f"Run data successfully exported to {file_name_input}.",
                               text_color="green")
            self.output_file_name.delete(0, "end")
            self.start_date_entry.delete(0, "end")
        except InvalidFolderPathError:
            self.msg.configure(text="Invalid folder path. Try using the browse feature.", text_color="red")
        except EmptyFileNameError:
            self.msg.configure(text="File name cannot be empty.", text_color="red")
        except ValueError:
            self.msg.configure(text="Invalid start date. Any non-empty input should be of the form YYYY-MM-DD.", text_color="red")
        except Exception as e:
            print("Unexpected error: " + str(e))

    def browse_for_folder_path(self) -> None:
        folder_path = filedialog.askdirectory()

        if folder_path:
            self.folder_path_entry.delete(0, "end")
            self.folder_path_entry.insert(0, folder_path)

class EmptyFileNameError(Exception):
    """
    Exception thrown when a file name is left empty or blank in an input field.
    """
    pass

class InvalidFolderPathError(Exception):
    """
    Exception thrown when a folder path is left empty or blank in an input field.
    """
    pass