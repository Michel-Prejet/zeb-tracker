import csv
from datetime import date

from domain.bus import Bus
from domain.fleet import Fleet
from domain.run import Run
from persistence.RunPersistence import save_runs
from utilities.InvariantHelper import require_not_none

RUN_DATE_INDEX = 0
BUS_TRACKING_NUM_INDEX = 1
BLOCK_ID_INDEX = 2

RED = "\033[31m"
COLOUR_RESET = "\033[0m"

def add_runs_to_fleet_from_csv(input_file: str, fleet: Fleet) -> None:
    """
    Adds runs to buses in a given fleet by reading lines from a given CSV
    input file. Each line in the file should correspond to a run formatted as
    RUN DATE (YYYY-MM-DD), BUS TRACKING NUMBER, BLOCK ID. Skips any malformed
    lines and prints feedback to the terminal which includes any exceptions,
    the number of lines skipped, and the total number of lines read.
    Assumes that the file contains a header row.

    :param input_file: the CSV file from which to read run data.
    :param fleet: the fleet to which to add runs.
    """
    require_not_none(input_file, "Input file should not be None.")
    require_not_none(fleet, "Fleet should not be None.")

    print("*** Starting CSV import ***")

    line_num = 0
    lines_skipped = 0
    added_runs: list[tuple[Run, Bus]] = []

    with open(input_file, newline="") as file:
        reader = csv.reader(file)

        next(reader) # Skip header

        for row in reader:
            line_num += 1
            print(f"\rProcessing line {line_num}", end="", flush=True)

            try:
                added_runs.append(_add_run_from_tokens(row, fleet))
            except Exception as e:
                lines_skipped += 1
                print(f"\n{RED}Error on line {line_num}: {type(e).__name__}")
        print()

    save_runs(added_runs)

    print(f"""{COLOUR_RESET}*** Completed CSV import ***
    Skipped {lines_skipped} out of {line_num} total lines.""")

def _add_run_from_tokens(tokens: list[str], fleet: Fleet) -> tuple[Run, Bus]:
    """
    Uses a given list of tokens to create a run and add it to a bus in the
    given fleet. Expects valid tokens for the run date, bus tracking
    number, and block ID (in that order), and assumes that a bus exists in the
    given fleet with that tracking number.

    :param tokens: the list of tokens (strings) from which to create a run and
    find the bus to add it to.
    :param fleet: the fleet containing the bus to which to add the run.
    :return: a tuple containing the added run and the bus it was added to in
    the form (RUN, BUS).
    """
    require_not_none(tokens, "Token list should not be None.")
    for token in tokens:
        require_not_none(token, "Token in token list should not be None.")
    require_not_none(fleet, "Fleet should not be None.")

    run_date: date = date.fromisoformat(tokens[RUN_DATE_INDEX])
    bus_tracking_num: int = int(tokens[BUS_TRACKING_NUM_INDEX])
    block_id: str = tokens[BLOCK_ID_INDEX]

    run = Run(block_id, run_date)
    bus = fleet.get_bus(bus_tracking_num)

    require_not_none(bus, f"No bus found with tracking number {bus_tracking_num}.")
    require_not_none(run, "Run should not be None after it is created.")

    bus.add_run(run)

    return run, bus