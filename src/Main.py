import customtkinter as ctk
from controller.FleetController import FleetController
from persistence.Connection import initialize_database, connection
from utilities.CSVImporter import add_runs_to_fleet_from_csv

DIMENSIONS = '600x450'
TITLE = 'ZEB Tracker'

# Create tables for the database
initialize_database(connection())

# Initialize window
app = ctk.CTk()
app.geometry(DIMENSIONS)
app.title(TITLE)

# Start controller
controller = FleetController(app)

add_runs_to_fleet_from_csv("../zeb-run-data.csv", controller.fleet)

app.mainloop()