 with 
 airports as (
     select *
     from {{ref("staging_airports")}}
 
 ), 
 departures as (
     select * 
     from {{ref("staging_departures")}}
 ),
 arrivals as (
     select * 
     from {{ref("staging_arrivals")}}
 ),
 raw_flights as (
     select * 
     from {{ref("staging_raw_flights")}}
 )
 select 
     rf.icao24,
     rf.departure_time_ts as departure_time_ts,
     rf.arrival_time_ts as arrival_time_ts,
     TIMESTAMP_SECONDS(rf.departure_time_ts) as departure_time,
     TIMESTAMP_SECONDS(rf.arrival_time_ts) as arrival_time,
     CAST(ad.id AS STRING) as departure_id,
     CAST(aa.id AS STRING) as arrival_id,
     ad.name as departure_name,
     ad.iso_country as departure_country,
     aa.name as arrival_name,
     aa.iso_country as arrival_country,
     TIMESTAMP_DIFF(TIMESTAMP_SECONDS(rf.arrival_time_ts),TIMESTAMP_SECONDS(rf.departure_time_ts), MINUTE) as duration,
     {{gcd_distance('ad.latitude_deg','ad.longitude_deg','aa.latitude_deg','aa.longitude_deg')}} as distance
 
 FROM
     raw_flights rf
 JOIN
     departures d
 ON
     1=1
     AND d.icao24 = rf.icao24
     AND d.time_position = rf.departure_time_ts
 LEFT JOIN
     arrivals a
 ON
     1=1
     AND rf.icao24 = a.icao24
     AND rf.arrival_time_ts = a.time_position
 
 LEFT JOIN 
     airports ad
 on
     ad.id= cast(d.id as int64)
 LEFT JOIN
     airports aa
 on
     aa.id= cast(a.id as int64)
 
 where 
     1=1
     and ad.id <> aa.id 