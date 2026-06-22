from datetime import date
from typing import Callable
import customtkinter as ctk
from logic.RunFiltering.RunFilterType import RunFilterType
from ui.UIConstants import SQUARE_BUTTON_WIDTH, SQUARE_BUTTON_HEIGHT, PADDING_MEDIUM, MEDIUM_BUTTON_WIDTH, \
    MEDIUM_BUTTON_HEIGHT, SPLIT_INPUT_FIELD_WIDTH, REGULAR_INPUT_FIELD_WIDTH
from utilities.InvariantHelper import require_not_none


INITIAL_SEARCH_FILTER = RunFilterType.DATE

class RunSearchFrame(ctk.CTkFrame):
    """
    Frame containing a search tool for a scrollable list of runs. Includes
    input field(s), search/reset search buttons, a search filter menu, and
    error messages.
    """

    def __init__(self, parent: ctk.CTkFrame, submit_search: Callable,
                 reset_search: Callable):
        require_not_none(parent, "Parent should not be None.")
        require_not_none(submit_search, "submit_search() should not be None.")
        require_not_none(reset_search, "reset_search() should not be None.")

        super().__init__(parent)

        self.submit_search = submit_search
        self.reset_search = reset_search

        self._configure_frame()
        self._initialize_input_fields()
        self._create_search_button()
        self._create_search_filter_menu()
        self._create_reset_button()
        self._initialize_error_message_label()

        self._refresh_input_fields_frame()

    def clear_input_fields(self) -> None:
        self.search_entry_main.delete(0, "end")
        self.search_entry_extra.delete(0, "end")

    def reset_search_filter_menu(self) -> None:
        """
        Resets the search filter menu to its initial value and reconstructs
        the input fields accordingly.
        """
        self.search_filter_menu.set(INITIAL_SEARCH_FILTER.value)
        self._refresh_input_fields_frame()

    def get_main_input_raw(self) -> str:
        return self.search_entry_main.get().strip()

    def get_date_from_main_input(self) -> date:
        """
        Gets the value in the main search input field and creates a datetime
        object. May raise a ValueError if the input is invalid.

        :return: a datetime object created from the main search input field.
        """
        date_raw = self.search_entry_main.get().strip()
        return date.fromisoformat(date_raw)

    def get_date_from_extra_input(self) -> date:
        """
        Gets the value in the secondary search input field and creates a
        datetime object. May raise a ValueError if the input is invalid.

        :return: a datetime object created from the secondary search input field.
        """
        date_raw = self.search_entry_extra.get().strip()
        return date.fromisoformat(date_raw)

    def get_search_filter_selection(self) -> RunFilterType:
        return RunFilterType(self.search_filter_menu.get())

    def show_error(self, message: str) -> None:
        """
        Displays a given error message in red text below the search input
        fields.
        """
        self.msg.configure(text=message, text_color="red")
        self.msg.grid(row=1, columnspan=3, sticky="w")

    def remove_error_message(self) -> None:
        self.msg.grid_forget()

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _initialize_input_fields(self) -> None:
        self.search_inputs_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.search_inputs_frame.grid(row=0, column=0, sticky="w")

        self.search_entry_main = ctk.CTkEntry(self.search_inputs_frame)
        self.search_entry_extra = ctk.CTkEntry(self.search_inputs_frame)

    def _create_search_button(self) -> None:
        ctk.CTkButton(
            self,
            text="🔎",
            width=SQUARE_BUTTON_WIDTH,
            height=SQUARE_BUTTON_HEIGHT,
            command=self.submit_search
        ).grid(row=0, column=1, sticky="w", padx=PADDING_MEDIUM)

    def _create_search_filter_menu(self) -> None:
        self.search_filter_menu = ctk.CTkOptionMenu(
            self,
            values=[f.value for f in RunFilterType],
            command=lambda _: self._refresh_input_fields_frame()
        )
        self.search_filter_menu.grid(
            row=0,
            column=2,
            sticky="w",
            padx=PADDING_MEDIUM
        )

    def _refresh_input_fields_frame(self) -> None:
        self.clear_input_fields()
        self.msg.grid_forget()
        self.search_inputs_frame.focus_set()

        if self.search_filter_menu.get() == RunFilterType.DATE.value:
            self._display_two_date_input_fields()
        else:
            self._display_one_general_input_field()

    def _display_two_date_input_fields(self) -> None:
        self.search_entry_main.configure(
            placeholder_text="Start date",
            width=SPLIT_INPUT_FIELD_WIDTH
        )
        self.search_entry_extra.configure(
            placeholder_text="End date",
            width=SPLIT_INPUT_FIELD_WIDTH
        )
        self.search_entry_main.pack(anchor="w", side="left")
        self.search_entry_extra.pack(anchor="w", padx=PADDING_MEDIUM)

    def _display_one_general_input_field(self) -> None:
        self.search_entry_extra.pack_forget()
        self.search_entry_main.configure(
            placeholder_text="Search...",
            width=REGULAR_INPUT_FIELD_WIDTH
        )
        self.search_entry_main.pack(anchor="w")

    def _create_reset_button(self) -> None:
        ctk.CTkButton(
            self,
            text="Reset",
            width=MEDIUM_BUTTON_WIDTH,
            height=MEDIUM_BUTTON_HEIGHT,
            command=self.reset_search
        ).grid(row=0, column=3, sticky="w", padx=PADDING_MEDIUM)

    def _initialize_error_message_label(self) -> None:
        self.msg = ctk.CTkLabel(self, text="")