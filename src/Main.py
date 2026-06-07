from datetime import timedelta

import customtkinter as ctk
from controller.FleetController import FleetController
from domain.location_info.Coordinates import Coordinates
from domain.location_info.LocationInfo import LocationInfo
from domain.location_info.Stop import Stop
from persistence.Connection import initialize_database, connection
from dotenv import load_dotenv

load_dotenv()

DIMENSIONS = '900x650'
TITLE = 'ZEB Tracker'

# Create tables for the database
initialize_database(connection())

# Initialize window
app = ctk.CTk()
app.geometry(DIMENSIONS)
app.title(TITLE)
app.iconbitmap("../icon.ico")

# Start controller
ctrl = FleetController(app)
# ctrl.fleet.get_bus(288).location_info = LocationInfo(
#     Stop("Northbound Pembina at Newdale North", 60032, Coordinates(1.0, 1.0)),
#     "BLUE",
#     "Unicity Hub",
#     "1-2",
#     timedelta(hours=17, minutes=11, seconds=2),
#     timedelta(hours=17, minutes=11, seconds=2)
# )
# ctrl.view_fleet_frame.notify()


app.mainloop()