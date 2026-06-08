from datetime import timedelta, datetime
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
FleetController(app)

app.mainloop()