create table if not exists bus(
    tracking_num integer not null unique,
    year integer not null,
    model varchar(255) not null
);

create table if not exists run(
    id serial not null unique,
    block_id varchar(255) not null,
    run_date date not null,
    bus integer not null,
    foreign key(bus) references bus(tracking_num)
        on delete cascade,
    unique(block_id, run_date, bus)
);