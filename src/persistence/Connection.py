import sqlite3
from pathlib import Path


def connection() -> sqlite3.Connection:
    """
    :return: a connection to the database for the application.
    """
    db = sqlite3.connect("../zeb-tracker.db")
    db.execute("PRAGMA foreign_keys = ON")

    return db

def initialize_database(db: sqlite3.Connection) -> None:
    """
    Runs the DDL for the database.

    :param db: the database for which to create tables.
    """
    ddl_path = Path(__file__).parent.parent.parent / "sql" / "create-tables.ddl"
    with open(ddl_path, "r") as ddl:
        db.executescript(ddl.read())
