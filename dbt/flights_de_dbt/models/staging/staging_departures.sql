with source_data as (

    select *
    from `flights`.departures_fact
    where
        1 = 1
        and not exists (
            select icao24, departure_time_ts
            from `flights`.flights_fact
        )

)

select *
from source_data