import sqlite3
from pathlib import Path


def connection():
    """
    Runs the DDL and returns a connection to the database.

    :return: a connection to the database for the application.
    """
    db = sqlite3.connect("zeb-tracker.db")
    db.execute("PRAGMA foreign_keys = ON")

    ddl_path = Path(__file__).parent.parent.parent / "sql" / "create-tables.ddl"
    with open(ddl_path, "r") as ddl:
        db.executescript(ddl.read())

    return db
