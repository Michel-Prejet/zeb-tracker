import customtkinter as ctk
from constants.ui_constants import LARGE_TITLE_FONT, PADDING_MEDIUM
from utilities.invariant_helper import require_not_none, require_state


MAX_ERROR_MESSAGES = 100

WINDOW_TITLE = "Error log"

WINDOW_DIMENSIONS = (500, 350)
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_DIMENSIONS

SCROLLABLE_LIST_DIMENSIONS = (WINDOW_WIDTH, WINDOW_HEIGHT - 50)
SCROLLABLE_LIST_WIDTH, SCROLLABLE_LIST_HEIGHT = SCROLLABLE_LIST_DIMENSIONS

class ErrorLog(ctk.CTkToplevel):
    """
    Dialog containing a list of error messages that occurred during a location
    fetch. A maximum of 100 error messages can be displayed.
    """

    def __init__(self, app: ctk.CTk, error_messages: list[str], controller):
        require_not_none(app, "App should not be None.")
        require_not_none(error_messages, "Error message list should not be None.")
        for msg in error_messages:
            require_not_none(msg, "Error message in list should not be None.")
            require_state(len(msg.strip()) > 0, "Error message in list should not be empty or only whitespace.")
        require_not_none(controller, "Controller should not be None.")

        super().__init__(app)

        self.app = app
        self.num_errors = len(error_messages)
        self.error_messages = error_messages
        self.controller = controller

        if self.num_errors > MAX_ERROR_MESSAGES:
            self.error_messages = self.error_messages[:MAX_ERROR_MESSAGES]

        self._configure_window()
        self._create_header()
        self._create_scrollable_list()

    def _configure_window(self) -> None:
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.transient(self.app)

    def _create_header(self) -> None:
        pluralization = "s"
        if self.num_errors == 1:
            pluralization = ""

        ctk.CTkLabel(
            self,
            text=f"⚠️ {self.num_errors} error{pluralization} occurred during location fetch",
            font=LARGE_TITLE_FONT
        ).pack(pady=PADDING_MEDIUM)

        if self.num_errors > MAX_ERROR_MESSAGES:
            ctk.CTkLabel(
                self,
                text="(Only the first 100 are shown)",
                font=ctk.CTkFont(weight="bold")
            ).pack()

    def _create_scrollable_list(self) -> None:
        scrollable_list = ctk.CTkScrollableFrame(
            self,
            width=SCROLLABLE_LIST_WIDTH,
            height=SCROLLABLE_LIST_HEIGHT,
            fg_color="transparent"
        )
        scrollable_list.pack()

        for msg in self.error_messages:
            ctk.CTkLabel(
                scrollable_list,
                text=msg
            ).pack(anchor="nw", pady=PADDING_MEDIUM)

