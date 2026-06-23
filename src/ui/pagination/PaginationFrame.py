import math
from typing import Callable
import customtkinter as ctk
from ui.pagination.Paginatable import Paginatable
from constants.ui_constants import SQUARE_BUTTON_WIDTH, SQUARE_BUTTON_HEIGHT, PADDING_SMALL, PADDING_MEDIUM
from utilities.InvariantHelper import require_not_none, require_state


class PaginationFrame(ctk.CTkFrame):
    """
    Child frame containing page information and pagination controls for a
    scrollable list. Displays the current page, the total number of pages,
    and the total number of items (with a method to refresh this information),
    along with buttons to go to the first page, the previous page, the next
    page, and the last page.
    """

    def __init__(self, parent: Paginatable, item_name: str,
                 items_per_page: int, get_num_items: Callable):
        require_not_none(parent, "Parent frame cannot be None.")
        require_state(isinstance(parent, ctk.CTkFrame),
                      "Parent should be a Custom Tkinter frame.")
        require_not_none(item_name, "Item name cannot be None.")
        require_not_none(items_per_page, "Number of items per page cannot be None.")
        require_state(items_per_page > 0, "Items per page must be a positive integer.")
        require_not_none(get_num_items, "get_num_items() cannot be None.")

        super().__init__(parent)

        self.parent = parent
        self.item_name = item_name
        self.items_per_page = items_per_page
        self.get_num_items = get_num_items

        self._configure_frame()
        self._create_page_information_and_controls()

    def num_pages(self) -> int:
        """
        :return: the number of pages needed to display all the items in the
        list.
        """
        num_items = self.get_num_items()

        if num_items == 0:
            return 1

        return math.ceil(num_items / self.items_per_page)

    def update_page_info(self, curr_page: int) -> None:
        """
        Updates the current page and the total number of pages displayed.
        """
        self.page_info.configure(
            text=f"Page {curr_page} of {self.num_pages()} ({self.get_num_items()} {self.item_name})"
        )

    def _configure_frame(self) -> None:
        self.configure(fg_color="transparent")

    def _create_page_information_and_controls(self) -> None:
        self.page_info = ctk.CTkLabel(self)
        self.page_info.pack(anchor="nw", padx=PADDING_MEDIUM)
        self.update_page_info(curr_page=1)

        self._create_page_button("<<", self.parent.first_page)
        self._create_page_button("<", self.parent.prev_page)
        self._create_page_button(">", self.parent.next_page)
        self._create_page_button(">>", self.parent.last_page)

    def _create_page_button(self, label: str, command: Callable) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=label,
            width=SQUARE_BUTTON_WIDTH,
            height=SQUARE_BUTTON_HEIGHT,
            command=command
        )
        button.pack(anchor="nw", side="left", padx=PADDING_SMALL)

        return button