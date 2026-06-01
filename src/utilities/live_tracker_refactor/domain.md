```mermaid
classDiagram
    class ObservationDict {
        %% Observations sorted by estimated arrival time
        -dict[tracking_num -> list~BusObservation~] bus_observations
        
        +get_all_observations_for_bus(tracking_num) list~BusObservation~
        +get_closest_observation_for_bus(tracking_num) BusObservation | None
        +add_observation(observation) None
    }

    ObservationDict --* BusObservation
    
    class BusObservation {
        -Stop stop
        -string route
        -string destination
        -int tracking_num
        -timedelta scheduled_arrival
        -timedelta estimated_arrival
    }
    
    BusObservation --o Stop
    
    note for BusObservation"Invariant properties:
    * stop != None
    * route != None
    * len(route) >= 1
    * destination != None
    * len(destination) >= 1
    * tracking_num != None
    * 100 <= tracking_num <= 999
    * scheduled_arrival != None
    * estimated_arrival != None
    "
    
    class Stop {
        -string name
        -int stop_id
        -Coordinate coordinates
    }
    
    Stop --* Coordinate

    note for Stop"Invariant properties:
    * name != None
    * len(name) >= 1
    * stop_id != None
    * len(stop_id) == 5
    * coordinates != None
    "
    
    class Coordinate {
        -float latitude
        -float longitude
    }
    
    note for Coordinate"Invariant properties:
    * latitude != None
    * -90 <= latitude <= 90
    * longitude != None
    * -180 <= longitude <= 180
    "
```