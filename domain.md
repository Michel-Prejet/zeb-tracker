# Domain Model

The following is a class diagram for the ZEB tracker application.

```mermaid
classDiagram
    class Fleet {
        -Dictionary~int, Bus~ buses
        
        +sorted_buses() List~Bus~
        +sorted_runs() List~Run~
        +runs_starting_at_date() List~Run~
        +num_runs() int
        +get_bus(tracking_num) Bus
        +add_bus(bus) void
        +remove_bus(bus) void
        +update_bus_locations(locations) void
    }
    
    note for Fleet"Invariant properties:
    * buses != None
    * for bus in buses, bus != None
    "
    
    Fleet --* Bus
    
    class Bus {
        -int tracking_num
        -int year
        -String model
        -Set~Run~ runs
        -dict location_info
        
        +add_run(run) void
        +remove_run(run) void
        +num_runs() int
        +first_run() Run
        +last_run() Run
    }

    note for Bus "Invariant properties:
    * tracking_num != None
    * 100 <= tracking_num <= 999
    * year != None
    * year >= 2000
    * model != None
    * model.length >= 1
    * runs != None
    * for run in runs, run != None
    "
    
    Bus --* Run
    
    class Run {
        -String block_id
        -date run_date
    }
    
    note for Run"Invariant properties:
    * block_id != None
    * block_id.length >= 1
    * run_date != None
    "
```