import csv
from datetime import date
from pathlib import Path
from domain.fleet import Fleet
from utilities.invariant_helper import require_not_none


def export_fleet_runs_to_csv(output_file: Path, fleet: Fleet,
                             start_date: date | None) -> None:
    """
    Writes each run in the given fleet to a given CSV file, where each row is
    of the form DATE (YYYY-MM-DD), BUS TRACKING NUMBER, BLOCK ID. Optionally,
    all runs before the given start date are omitted in the CSV file.

    :param output_file: the path of the file in which to write the run list.
    :param fleet: the fleet containing list of runs to write to the output file.
    :param start_date: all runs occurring before this date will be omitted from
    the file (optional).
    """
    require_not_none(output_file, "Output file should not be None.")
    require_not_none(fleet, "Fleet should not be None.")

    if start_date is not None:
        run_assignments = fleet.get_runs_starting_from(start_date)
    else:
        run_assignments = fleet.runs

    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Date", "Bus", "Block ID"])

        for assignment in reversed(run_assignments):
            writer.writerow(
                [
                    str(assignment.date),
                    assignment.tracking_num,
                    assignment.block_id
                ]
            )
