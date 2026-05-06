create table if not exists bus(
    tracking_num integer not null unique,
    year integer not null,
    model text not null
);

create table if not exists run(
    id integer primary key autoincrement,
    block_id text not null,
    run_date text not null,
    bus integer not null,
    foreign key(bus) references bus(tracking_num)
        on delete cascade,
    unique(block_id, run_date, bus)
);