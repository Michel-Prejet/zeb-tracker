import customtkinter as ctk
from controller.FleetController import FleetController

DIMENSIONS = '1280x720'
TITLE = 'ZEB Tracker'

# Initialize window
app = ctk.CTk()
app.geometry(DIMENSIONS)
app.title(TITLE)

# Start controller
FleetController(app)

app.mainloop()