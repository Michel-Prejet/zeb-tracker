from persistence.Connection import connection
from domain.Bus import Bus
from utilities.InvariantHelper import require_not_none
from persistence.RunPersistence import load_runs_for_bus


def save_bus(bus: Bus) -> None:
    """
    Saves a given bus to the database. If a bus already exists in the
    database with the same tracking number, no action is taken.

    :param bus: the bus object to save to the database.
    """
    require_not_none(bus, "Bus should not be None.")

    with connection() as db:
        with db.cursor() as cursor:
            cursor.execute(
                """
                insert into bus(tracking_num, year, model) values(%s, %s, %s)
                on conflict do nothing
                """,
                (bus.tracking_num, bus.year, bus.model)
            )
        db.commit()

def delete_bus(bus: Bus) -> None:
    """
    Deletes a given bus from the database. No action is taken if no
    bus exists with the same tracking number in the database.

    :param bus: the bus to delete from the database.
    """
    require_not_none(bus, "Bus should not be None.")

    with connection() as db:
        with db.cursor() as cursor:
            cursor.execute(
                """
                delete from bus where tracking_num=%s
                """,
                (bus.tracking_num,)
            )
        db.commit()

def load_all_buses() -> list[Bus]:
    """
    Loads all buses in the database and creates a list of Bus objects.

    :return: a list of Bus objects containing all buses in the database
    (including their runs).
    """
    buses: list[Bus] = []

    with connection() as db:
        with db.cursor() as cursor:
            cursor.execute(
                """
                select tracking_num, year, model from bus
                """
            )

            for row in cursor.fetchall():
                tracking_num, year, model = row
                curr_bus = Bus(tracking_num, year, model)

                for curr_run in load_runs_for_bus(curr_bus):
                    curr_bus.add_run(curr_run)

                buses.append(curr_bus)

    return buses
