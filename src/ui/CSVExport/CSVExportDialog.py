from datetime import date
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from domain.Fleet import Fleet
from ui.CSVExport.CSVExportDialogErrors import InvalidFolderPathError, EmptyFileNameError, InvalidRunDataStartDateError
from ui.UIConstants import LARGE_TITLE_FONT, PADDING_LARGE, PADDING_MEDIUM, SQUARE_BUTTON_WIDTH, SQUARE_BUTTON_HEIGHT
from utilities.InvariantHelper import require_not_none
from utilities.csv_io.CSVExporter import create_csv_from_fleet


WINDOW_TITLE = "Export to CSV"

WINDOW_DIMENSIONS = (500, 250)
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_DIMENSIONS

LABEL_COL = 0
INPUT_FIELD_COL = 1

ERR_MESSAGES = {
    InvalidFolderPathError: "Invalid folder path. Try using the browse feature.",
    EmptyFileNameError: "File name cannot be empty.",
    InvalidRunDataStartDateError: "Invalid start date. Any non-empty input should be of the form YYYY-MM-DD."
}

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

        self.app = app
        self.fleet = fleet

        self._configure_window()
        self._create_header()
        self._create_input_fields()
        self._create_submit_area()

    def _submit(self) -> None:
        """
        Attempts to create a CSV file containing all run data for this fleet with
        the folder path, name, and (optionally) the start date provided in the
        input fields. Prints an error message if the folder path or the file
        name are empty, if the folder path is invalid or doesn't exist, or if
        the start date is non-empty and not of the form YYYY-MM-DD. Otherwise,
        a success message is displayed.
        """
        try:
            filename = self._get_filename_input()
            file_path = self._get_output_file_path(filename)
            start_date = self._get_start_date_input()

            create_csv_from_fleet(file_path, self.fleet, start_date)

            self._show_success(
                f"Run data successfully exported to {filename}."
            )
            self._clear_input_fields()
        except Exception as e:
            self._handle_error(e)

    def _configure_window(self) -> None:
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.transient(self.app)

    def _create_header(self) -> None:
        ctk.CTkLabel(
            self,
            text="Export run data to CSV",
            font=LARGE_TITLE_FONT
        ).pack()

    def _create_input_fields(self) -> None:
        self.inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inputs_frame.pack(anchor="nw", pady=PADDING_LARGE)

        self.folder_path_entry = self._add_labelled_input_field(
            label="File path",
            row=1
        )
        self._add_browse_file_explorer_button()

        self.output_file_name_entry = self._add_labelled_input_field(
            label="Output file name",
            row=2,
            placeholder="e.g. runs.csv"
        )

        self.start_date_entry = self._add_labelled_input_field(
            label="Start date (optional)",
            row=3,
            placeholder="e.g. 2026-05-01"
        )

    def _add_labelled_input_field(self, label: str, row: int, placeholder: str = "") -> ctk.CTkEntry:
        label = ctk.CTkLabel(
            self.inputs_frame,
            text=label
        )
        label.grid(
            row=row,
            column=LABEL_COL,
            sticky="w",
            padx=PADDING_MEDIUM
        )

        entry = ctk.CTkEntry(
            self.inputs_frame,
            placeholder_text=placeholder
        )
        entry.grid(
            row=row,
            column=INPUT_FIELD_COL,
            sticky="w",
            padx=PADDING_MEDIUM
        )

        return entry

    def _add_browse_file_explorer_button(self) -> None:
        ctk.CTkButton(
            self.inputs_frame,
            text="📂",
            command=self._browse_for_folder_path,
            width=SQUARE_BUTTON_WIDTH,
            height=SQUARE_BUTTON_HEIGHT
        ).grid(row=1, column=2, sticky="w", padx=PADDING_MEDIUM)

    def _browse_for_folder_path(self) -> None:
        folder_path = filedialog.askdirectory()

        if folder_path:
            self.folder_path_entry.delete(0, "end")
            self.folder_path_entry.insert(0, folder_path)

    def _create_submit_area(self) -> None:
        ctk.CTkButton(
            self,
            text="Export",
            command=self._submit
        ).pack()

        self.msg = ctk.CTkLabel(self, text="")
        self.msg.pack()

    def _get_filename_input(self) -> str:
        FILE_EXTENSION = ".csv"

        filename_input = self.output_file_name_entry.get().strip()

        if len(filename_input) == 0:
            raise EmptyFileNameError()

        if not filename_input.endswith(FILE_EXTENSION):
            filename_input += FILE_EXTENSION

        return filename_input

    def _get_output_file_path(self, filename: str) -> Path:
        folder_path_input = self.folder_path_entry.get().strip()

        if len(folder_path_input) == 0:
            raise InvalidFolderPathError()

        folder_path = Path(folder_path_input)

        if not folder_path.exists() or not folder_path.is_dir():
            raise InvalidFolderPathError()

        return folder_path / filename

    def _get_start_date_input(self) -> date | None:
        start_date_input = self.start_date_entry.get().strip()

        if len(start_date_input) == 0:
            return None

        try:
            start_date = date.fromisoformat(start_date_input)
        except ValueError:
            raise InvalidRunDataStartDateError()

        return start_date

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
        self.folder_path_entry.delete(0, "end")
        self.output_file_name_entry.delete(0, "end")
        self.start_date_entry.delete(0, "end")