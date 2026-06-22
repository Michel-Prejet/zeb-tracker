import customtkinter as ctk
from domain.Bus import Bus
from ui.UIConstants import PADDING_MEDIUM
from utilities.DateTimeHelper import format_timedelta
from utilities.InvariantHelper import require_not_none
import webbrowser


WINDOW_TITLE = "Location Info for Bus"
WINDOW_DIMENSIONS = (450, 200)
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_DIMENSIONS

LABEL_COL = 0
INFO_COL = 1

BLUE_LINK_COLOUR = "#3b8ed0"

class LocationInfoDialog(ctk.CTkToplevel):
    """
    Dialog containing location info for a given bus, including the block ID,
    the route & destination, and stop info (ID, name, ETA).
    """

    def __init__(self, app: ctk.CTk, bus: Bus):
        require_not_none(app, "App should not be None.")
        require_not_none(bus, "Bus should not be None.")
        require_not_none(bus.location_info,
                         "Bus location info should not be None.")

        super().__init__(app)

        self.app = app
        self.bus = bus
        self.info = bus.location_info

        self._configure_window()
        self._create_location_info_rows()
        self._create_google_maps_button()

    def _configure_window(self) -> None:
        self.title(f"{WINDOW_TITLE} {self.bus.tracking_num}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.transient(self.app)

    def _create_location_info_rows(self) -> None:
        block_id_info = "Unknown"
        if self.info.block_id is not None:
            block_id_info = self.info.block_id

        self._add_row(
            label="Block ID",
            content=block_id_info,
            row=0
        )

        self._add_row(
            label="Route",
            content=f"{self.info.route} to {self.info.destination}",
            row=1
        )

        self._add_row(
            label="Current stop",
            content=f"{self.info.stop.stop_id}",
            row=2
        )
        self._add_row(
            label="",
            content=self.info.stop.name,
            row=3
        )
        self._add_row(
            label="",
            content=f"ETA: {format_timedelta(self.info.estimated_departure)}",
            row=4
        )

    def _add_row(self, label: str, content: str, row: int) -> None:
        ctk.CTkLabel(
            self,
            text=label,
            text_color="gray"
        ).grid(column=LABEL_COL, row=row, sticky="w", padx=PADDING_MEDIUM)

        ctk.CTkLabel(
            self,
            text=content
        ).grid(column=INFO_COL, row=row, sticky="w", padx=PADDING_MEDIUM)

    def _create_google_maps_button(self) -> None:
        button = ctk.CTkLabel(
            self,
            text="Open in Google Maps",
            font=ctk.CTkFont(size=13, underline=True),
            text_color=BLUE_LINK_COLOUR
        )
        button.bind(
            "<Button-1>",
            lambda e: self._open_google_maps()
        )

        button.grid(column=INFO_COL, row=5, sticky="w", padx=PADDING_MEDIUM)

    def _open_google_maps(self) -> None:
        """
        Opens a link to the coordinates in Google Maps corresponding to the
        stop coordinates stored in this bus's location info.
        """
        url = (f"https://www.google.com/maps/search/?api=1&query="
               f"{self.info.stop.coordinates.latitude},"
               f"{self.info.stop.coordinates.longitude}")
        webbrowser.open(url)