import customtkinter as ctk
from controller.FleetController import FleetController
from persistence.Connection import initialize_database, connection
from dotenv import load_dotenv
from utilities.live_tracker.StopScanner import get_live_bus_locations

load_dotenv()

DIMENSIONS = '800x535'
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

# locations = get_live_bus_locations()
# for bus in locations.keys():
#     info = locations[bus]
#     print(f"Bus {bus} on route {info["route"]} to {info["destination"]} "
#           f"approaching {info["stop_name"]}.")
