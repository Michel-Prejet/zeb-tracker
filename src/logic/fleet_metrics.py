from domain.bus import Bus
from domain.fleet import Fleet
from utilities.invariant_helper import require_not_none, require_state


def bus_run_percentage(fleet: Fleet, bus: Bus) -> float:
    """
    Calculates the percentage of runs completed by a given bus in a given
    fleet, assuming that the bus comes from that fleet.
    """
    require_not_none(fleet, "Fleet should not be None.")
    require_not_none(bus, "Bus should not be None.")

    bus_in_fleet = fleet.get_bus(bus.tracking_num)

    if bus_in_fleet is None:
        return 0

    require_state(bus_in_fleet is bus,
                  "Bus should be the same object as the bus in the fleet.")

    if fleet.num_runs() == 0:
        return 0

    return (bus.num_runs() / fleet.num_runs()) * 100