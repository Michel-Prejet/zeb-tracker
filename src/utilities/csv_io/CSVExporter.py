import csv
from domain.Bus import Bus
from domain.Run import Run
from utilities.InvariantHelper import require_not_none


def create_csv_from_fleet(output_file: str, run_list: list[tuple[Run, Bus]]) -> None:
    """
    Writes each run in the given tuple list to a given CSV file, where each row is
    of the form DATE (YYYY-MM-DD), BUS TRACKING NUMBER, BLOCK ID.

    :param output_file: the name of the file in which to write the run list.
    :param run_list: the list of runs to write to the output file.
    """
    require_not_none(output_file, "Output file should not be None.")
    require_not_none(run_list, "Run list should not be None.")

    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Date", "Bus", "Block ID"])

        for run in run_list[::-1]:
            writer.writerow([str(run[0].run_date), run[1].tracking_num, run[0].block_id])
