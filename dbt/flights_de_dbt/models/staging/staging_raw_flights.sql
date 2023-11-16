with 
departures as (
    select * 
    from {{ref("staging_departures")}}
),
arrivals as (
    select * 
    from {{ref("staging_arrivals")}}
)
SELECT
    d.icao24 as icao24,
    d.time_position as departure_time_ts,
    MIN(a.time_position) as arrival_time_ts
  FROM
    departures d 
  LEFT JOIN
   arrivals a 
  ON
    d.icao24 = a.icao24
    AND a.time_position >= d.time_position
  GROUP BY
    d.icao24, d.time_position