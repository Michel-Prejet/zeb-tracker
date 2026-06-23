import customtkinter as ctk
from controller.FleetController import FleetController
from persistence.Connection import initialize_database, connection
from dotenv import load_dotenv
from constants.ui_constants import APP_HEIGHT, APP_WIDTH

load_dotenv()


DIMENSIONS = f"{APP_WIDTH}x{APP_HEIGHT}"
TITLE = "ZEB Tracker"

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