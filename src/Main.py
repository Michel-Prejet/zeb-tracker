import customtkinter as ctk
from controller.FleetController import FleetController
from persistence.Connection import initialize_database, connection

DIMENSIONS = '800x650'
TITLE = 'ZEB Tracker'

# Create tables for the database
initialize_database(connection())

# Initialize window
app = ctk.CTk()
app.geometry(DIMENSIONS)
app.title(TITLE)

# Start controller
FleetController(app)

app.mainloop()