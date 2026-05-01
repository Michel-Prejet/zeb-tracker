# Domain Model

The following is a class diagram for the ZEB tracker application.

```mermaid
classDiagram
    class Fleet {
        -List~Bus~ buses
        
        +numRuns() int
        +getBus(trackingNum) Bus
        +addBus(bus) void
    }
    
    Fleet --* Bus
    
    class Bus {
        -int trackingNumber
        -int year
        -String model
        -List~Run~ runs
        
        +addRun(run) void
        +numRuns() int
        +routes() List~String~
        +firstRun() Run
        +lastRun() Run
    }

    note for Bus "Invariant properties:
    * trackingNumber >= 100
    * trackingNumber <= 999
    * year >= 2000
    * model.length >= 1
    "
    
    Bus --* Run
    
    class Run {
        -String blockID
        -DateTime start
        -DateTime end
        -List~String~ routes
        
        +date() String
    }
    
    note for Run"Invariant properties:
    * blockID.length >= 1
    * start.date == end.date
    * start < end
    * routes.length >= 1
    "
```