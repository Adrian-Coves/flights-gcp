with source_data as (

    select 
        id,
        ident,
        type,
        name,
        latitude_deg,
        longitude_deg,
        elevation_ft,
        continent,
        iso_country,
        iso_region,
        municipality,
        scheduled_service,
        gps_code,
        iata_code,
        local_code,
        home_link,
        wikipedia_link,
        keywords
    from `flights`.airports_dim
    where
        1 = 1
        and type like '%airport'
)

select *
from source_data