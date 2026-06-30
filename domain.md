# Domain Model

The following is a class diagram for the ZEB tracker application.

```mermaid
classDiagram
    class Fleet {
        -Dictionary[int, Bus] buses
        
        +buses() list~Bus~
        +runs() list~Run~
        +num_runs() int
        +get_bus(tracking_num) Bus
        +get_runs_starting_from(date) list[RunAssignment]
        +add_bus(bus) None
        +remove_bus(bus) None
        +add_run(run_assignment) None
        +remove_run(run_assignment) None
        +set_bus_location_info(tracking_num, info) None
        +reset_bus_location_info(tracking_num) None
    }
    
    note for Fleet"Invariant properties:
    * buses != None
    * for key, value in buses 
    *   key != None
    *   100 <= key <= 999
    *   value != None
    *   key == value.tracking_num
    "
    
    Fleet --* Bus

    class InferredRunList {
        -Fleet fleet
        -Dictionary[int, list~RunAssignment~] runs

        +inferred_runs() list~RunAssignment~
        +buses() list~Bus~
        +add_inferred_run(run_assignment) None
        +remove_inferred_run(run_assignment, notify) None
        +commit(run_assignment, notify) bool
        +commit_all() list~RunAssignment~
    }

    note for InferredRunList"Invariant properties:
    * fleet != None
    * runs != None
    * for key, value in runs:
    *   key != None
    *   100 <= key <= 999
    *   value != None
    *   len(value) >= 1
    *   for assigned_run in value:
    *       assigned_run != None
            assigned_run.tracking_num == key
    "

    InferredRunList --o Run
    InferredRunList --o Fleet
    
    class Bus {
        -int tracking_num
        -int year
        -String model
        -list~Run~ runs
        -LocationInfo location_info
        
        +tracking_num() int
        +year() int
        +model() str
        +runs() list~Run~
        +location_info() LocationInfo | None
        +num_runs() int
        +first_run() Run | None
        +last_run() Run | None
        +contains() bool
        +set_location_info(info) None
        +reset_location_info() None
        +add_run(run) None
        +remove_run(run) None
    }

    note for Bus "Invariant properties:
    * tracking_num != None
    * 100 <= tracking_num <= 999
    * year != None
    * year >= 1900
    * model != None
    * len(model) >= 1
    * runs != None
    * for run in runs, run != None
    "
    
    Bus --* Run
    
    class Run {
        -String block_id
        -date run_date
        
        +block_id() str
        +run_date() date
    }
    
    note for Run"Invariant properties:
    * block_id != None
    * len(block_id) >= 1
    * run_date != None
    "
    
    class RunAssignment {
        -Run run
        -Bus bus
        
        +run() Run
        +bus() Bus
        +date() date
        +tracking_num() int
        +block_id() str
    }
    
    RunAssignment --o Run
    RunAssignment --o Bus
    
    class LocationInfo {
        -Stop stop
        -string route
        -string destination
        -string block_id
        -timedelta scheduled_departure
        -timedelta scheduled_arrival
        -datetime query_time
        
        +stop() Stop
        +route() str
        +destination() str
        +block_id() str
        +scheduled_departure() timedelta
        +scheduled_arrival() timedelta
        +query_time() datetime
    }
    
    Bus --* LocationInfo
    
    note for LocationInfo"Invariant properties:
    * stop != None
    * route != None
    * len(route) >= 1
    * destination != None
    * len(destination) >= 1
    * if block_id is not None: len(block_id) >= 1
    * scheduled_departure != None
    * scheduled_arrival != None
    * query_time != None
    "
    
    class Stop {
        -string name
        -int stop_id
        -Coordinates coordinates
        
        +name() str
        +stop_id() int
        +coordinates() Coordinates
    }
    
    LocationInfo --* Stop
    
    note for Stop"Invariant properties:
    * name != None
    * len(name) >= 1
    * 1000 <= stop_id <= 9999
    * coordinates != None    
    "
    
    class Coordinates {
        -float latitude
        -float longitude
        
        +latitude() float
        +longitude() float
    }
    
    Stop --* Coordinates
    
    note for Coordinates"Invariant properties:
    * latitude != None
    * longitude != None
    * -90 <= latitude <= 90
    * -180 <= longitude <= 180
    "
```