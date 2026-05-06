from datetime import date

from domain.Bus import Bus
from persistence.Connection import connection
from domain.Run import Run
from utilities.InvariantHelper import require_not_none


def save_run(run: Run, bus: Bus) -> None:
    """
    Saves a given run completed by a given bus to the database. Takes no action
    if a run already exists in the database with the same block ID, date, and
    bus. If the run is saved, its ID attribute will be updated to the ID
    assigned by the database.

    :param run: the run to save to the database.
    :param bus: the bus that owns the given run.
    """
    require_not_none(run, "Run should not be None.")

    with connection() as db:
        cursor = db.cursor()
        cursor.execute(
            """
            insert into run(block_id, run_date, bus) values(?, ?, ?)
            on conflict do nothing returning id
            """,
            (run.block_id, run.run_date.isoformat(), bus.tracking_num)
        )
        row = cursor.fetchone()
        db.commit()

        if row is not None:
            run.id = row[0]

def save_runs(runs: list[tuple[Run, Bus]]) -> None:
    """
    Saves a given list of (Run, Bus) tuples to the database. Skips any run
    that already exists in the database with the same block ID, date, and
    bus. If the run is saved, its ID attribute will be updated to the ID
    assigned by the database.

    :param runs: a list of (Run, Bus) tuples each containing a run to save
    to the database along with its respective bus.
    """
    RUN_INDEX = 0
    BUS_INDEX = 1

    require_not_none(runs, "(Run, Bus) tuple list should not be None.")
    for run in runs:
        require_not_none(run[RUN_INDEX], "Run in tuple should not be None.")
        require_not_none(run[BUS_INDEX], "Bus in tuple should not be None.")

    with connection() as db:
        cursor = db.cursor()
        for run in runs:
            cursor.execute(
                """
                insert into run(block_id, run_date, bus) values(?, ?, ?)
                    on conflict do nothing returning id
                """,
                (run[RUN_INDEX].block_id,
                 run[RUN_INDEX].run_date.isoformat(),
                 run[BUS_INDEX].tracking_num)
            )
            row = cursor.fetchone()

            if row is not None:
                run[RUN_INDEX].id = row[0]

        db.commit()

def delete_run(run: Run) -> None:
    """
    Deletes a given run from the database. Assumes that the run has been
    assigned an ID (which it should if it was previously saved). Takes no
    action if no run with the same ID exists in the database.

    :param run: the run to delete from the database.
    """
    require_not_none(run, "Run should not be None.")
    require_not_none(run.id, "Run ID should not be None.")

    with connection() as db:
        cursor = db.cursor()
        cursor.execute(
            """
            delete from run where id=?
            """,
            (run.id,)
        )
        db.commit()

def load_runs_for_bus(bus: Bus) -> list[Run]:
    """
    Loads all runs for the given bus from the database and creates a list
    of Run objects.

    :param bus: the bus for which to load all runs from the database.
    :return: a list of Run containing all runs stored in the database for
    the given bus.
    """
    require_not_none(bus, "Bus should not be None.")

    runs: list[Run] = []

    with connection() as db:
        cursor = db.cursor()
        cursor.execute(
            """
            select id, block_id, run_date from run where bus=?
            """,
            (bus.tracking_num,)
        )

        for row in cursor.fetchall():
            run_id, block_id, run_date = row
            curr_run = Run(block_id, date.fromisoformat(run_date))
            curr_run.id = run_id

            runs.append(curr_run)

    return runs