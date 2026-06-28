from datetime import date
from domain.bus import Bus
from domain.run_assignment import RunAssignment
from persistence.connection import connection
from domain.run import Run
from utilities.InvariantHelper import require_not_none


def save_run(run_assignment: RunAssignment) -> None:
    """
    Saves a given run assignment to the database. Takes no action if a run
    already exists in the database with the same block ID, date, and bus.
    If the run is saved, its ID attribute will be updated to the ID assigned
    by the database.

    :param run_assignment: the run assignment to save to the database.
    """
    require_not_none(run_assignment, "Run assignment should not be None.")

    with connection() as db:
        cursor = db.cursor()
        cursor.execute(
            """
            insert into run(block_id, run_date, bus) values(?, ?, ?)
            on conflict do nothing returning id
            """,
            (run_assignment.block_id,
             run_assignment.date.isoformat(),
             run_assignment.tracking_num)
        )
        row = cursor.fetchone()
        db.commit()

        if row is not None:
            run_assignment.run.id = row[0]

def save_runs(runs: list[RunAssignment]) -> None:
    """
    Saves a given list of run assignments to the database. Skips any run
    that already exists in the database with the same block ID, date, and
    bus. If the run is saved, its ID attribute will be updated to the ID
    assigned by the database.

    :param runs: a list of run assignments each containing a run to save
    to the database along with its respective bus.
    """
    require_not_none(runs, "Run assignment list should not be None.")
    for run_assignment in runs:
        require_not_none(run_assignment, "Run assignment in list should not be None.")

    with connection() as db:
        cursor = db.cursor()
        for run_assignment in runs:
            cursor.execute(
                """
                insert into run(block_id, run_date, bus) values(?, ?, ?)
                    on conflict do nothing returning id
                """,
            (run_assignment.block_id,
             run_assignment.date.isoformat(),
             run_assignment.tracking_num)
            )
            row = cursor.fetchone()

            if row is not None:
                run_assignment.run.id = row[0]

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