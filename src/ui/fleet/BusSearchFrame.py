from typing import Callable
import customtkinter as ctk
from logic.bus_filtering.bus_filter_type import BusFilterType
from constants.ui_constants import REGULAR_INPUT_FIELD_WIDTH, SQUARE_BUTTON_WIDTH, SQUARE_BUTTON_HEIGHT, PADDING_MEDIUM, \
    MEDIUM_BUTTON_WIDTH, MEDIUM_BUTTON_HEIGHT, CHECKBOX_WIDTH, CHECKBOX_HEIGHT, CHECKBOX_BORDER_WIDTH


INITIAL_SEARCH_FILTER = BusFilterType.TRACKING_NUM

class BusSearchFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, submit_search: Callable,
                 reset_search: Callable, show_only_active: Callable):
        super().__init__(parent)

        self.submit_search = submit_search
        self.reset_search = reset_search
        self.show_only_active = show_only_active

        self._configure_frame()
        self._create_input_field()
        self._create_search_button()
        self._create_search_filter_menu()
        self._create_reset_button()
        self._create_show_only_active_checkbox()

    def reset(self) -> None:
        """
        Resets the search filter menu to its initial value, clears the
        input field, and deselects the Show Only Active checkbox.
        """
        self.reset_search_filter_menu()
        self.search_entry.delete(0, "end")
        self.show_only_active_checkbox.deselect()

    def reset_search_filter_menu(self) -> None:
        """
        Resets the search filter menu to its initial value.
        """
        self.search_filter_menu.set(INITIAL_SEARCH_FILTER.value)

    def get_input(self) -> str:
        return self.search_entry.get().strip()

    def get_search_filter_selection(self) -> BusFilterType:
        return BusFilterType(self.search_filter_menu.get())

    def get_show_only_active_selection(self) -> bool:
        return bool(self.show_only_active_checkbox.get())

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _create_input_field(self) -> None:
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search...",
            width=REGULAR_INPUT_FIELD_WIDTH
        )
        self.search_entry.grid(row=0, column=0, sticky="w")

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
            values=[f.value for f in BusFilterType]
        )
        self.search_filter_menu.grid(
            row=0,
            column=2,
            sticky="w",
            padx=PADDING_MEDIUM
        )

        self.reset_search_filter_menu()

    def _create_reset_button(self) -> None:
        ctk.CTkButton(
            self,
            text="Reset",
            width=MEDIUM_BUTTON_WIDTH,
            height=MEDIUM_BUTTON_HEIGHT,
            command=self.reset_search
        ).grid(row=0, column=3, sticky="w", padx=PADDING_MEDIUM)

    def _create_show_only_active_checkbox(self) -> None:
        self.show_only_active_checkbox = ctk.CTkCheckBox(
            self,
            text="Active buses only",
            checkbox_width=CHECKBOX_WIDTH,
            checkbox_height=CHECKBOX_HEIGHT,
            border_width=CHECKBOX_BORDER_WIDTH,
            command=self.show_only_active
        )
        self.show_only_active_checkbox.grid(
            row=0,
            column=4,
            sticky="w",
            padx=PADDING_MEDIUM
        )