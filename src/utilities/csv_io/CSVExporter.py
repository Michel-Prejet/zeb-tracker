import csv
from datetime import date
from pathlib import Path
from domain.Fleet import Fleet
from utilities.InvariantHelper import require_not_none


def create_csv_from_fleet(output_file: Path, fleet: Fleet, start_date: date | None) -> None:
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
        runs = fleet.runs_starting_at_date(start_date)
    else:
        runs = fleet.sorted_runs()

    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Date", "Bus", "Block ID"])

        for entry in runs[::-1]:
            run, bus = entry
            writer.writerow([str(run.run_date), bus.tracking_num, run.block_id])
