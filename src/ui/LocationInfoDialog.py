import customtkinter as ctk
from domain.Bus import Bus
from utilities.InvariantHelper import require_not_none
import webbrowser


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
        self.bus = bus
        self.info = bus.location_info

        self.title(f"Location Info for Bus {bus.tracking_num}")
        self.geometry("400x200")
        self.transient(app)

        # Block ID
        (ctk.CTkLabel(self, text="Block ID", text_color="gray")
         .grid(column=0, row=0, sticky="w", padx=5))
        block_id_label = ctk.CTkLabel(self, text="Unknown")
        if self.info.block_id is not None:
            block_id_label.configure(text=self.info.block_id)
        block_id_label.grid(column=1, row=0, sticky="w", padx=5)

        # Route & Destination
        (ctk.CTkLabel(self, text="Route", text_color="gray")
         .grid(column=0, row=1, sticky="w", padx=5))
        (ctk.CTkLabel(self, text=f"{self.info.route} to {self.info.destination}")
         .grid(column=1, row=1, sticky="w", padx=5))

        # Stop Info
        (ctk.CTkLabel(self, text="Current stop", text_color="gray")
         .grid(column=0, row=2, sticky="w", padx=5))
        (ctk.CTkLabel(self, text=f"{self.info.stop.stop_id}")
         .grid(column=1, row=2, sticky="w", padx=5))
        (ctk.CTkLabel(self, text=self.info.stop.name)
         .grid(column=1, row=3, sticky="w", padx=5))
        (ctk.CTkLabel(self, text=f"ETA: {self.info.estimated_departure}")
         .grid(column=1, row=4, sticky="w", padx=5))

        # Google maps button
        maps_button = ctk.CTkLabel(
            self,
            text="Open in Google Maps",
            font=ctk.CTkFont(size=13, underline=True),
            text_color="#3b8ed0"
        )
        maps_button.bind("<Button-1>",
                         lambda e: self._open_google_maps())
        maps_button.grid(column=1, row=5, sticky="w", padx=5)

    def _open_google_maps(self) -> None:
        """
        Opens a link to the coordinates in Google Maps corresponding to the
        stop coordinates stored in this bus's location info.
        """
        url = (f"https://www.google.com/maps/search/?api=1&query="
               f"{self.info.stop.coordinates.latitude},"
               f"{self.info.stop.coordinates.longitude}")
        webbrowser.open(url)