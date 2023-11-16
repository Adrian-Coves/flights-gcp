import sys
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, lead, lag
import pyspark.sql.functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    BooleanType,
    FloatType,
)


def get_current_hour_date(filename: str) -> str:
    """Gets the date of the hour calculated with the format "%Y-%m-%d-%H"

    Args:
        filename (str): The filename passed as an argument

    Returns:
        str: The date with the format "%Y-%m-%d-%H"
    """
    date = filename.split("/")[-1]
    date = date.split("_")[0]
    return date


def get_previous_hour_filename(filename: str) -> str:
    """Calculates the filename from previous hour

    Args:
        filename: Current hour filename

    Returns:
        str: Previous hour filename
    """
    file_split = filename.split("/")
    date = file_split[-1]
    route = "/".join(file_split[:-1])
    date, endfile = date.split("_")[0], date.split("_")[1]
    n_date = datetime.strptime(date, "%Y-%m-%d-%H")

    previos_hour = n_date - timedelta(hours=1)
    previos_hour = previos_hour.strftime("%Y-%m-%d-%H")
    return f"{route}/{previos_hour}_{endfile}"


def explode_flights_df(df):
    """Explode info about flights dataframe

    Gets for each flight and position, the previous and next time it appears
    the same flight.
    Gets if the following instance is from the current hour.
    Gets if the following position is on ground

    Args:
        df (Dataframe): _description_

    Returns:
        Dataframe: _description_
    """
    windowSpec = Window.partitionBy("icao24").orderBy("time_position")
    exploded_df = (
        df.select("icao24", "time_position", "onground", "lon", "lat", "is_actual_df")
        .withColumn("next_on_ground", lead("onground").over(windowSpec))
        .withColumn("next_actual_df", lead("is_actual_df").over(windowSpec))
        .withColumn("previous_time_position", lag("time_position").over(windowSpec))
        .withColumn("next_time_position", lead("time_position").over(windowSpec))
    )
    return exploded_df


def get_departures_df(df):
    """Gets the departures from the flights posidtion dataframe

    First departure condition: Flights that were on ground and
    next timestamp is not on ground and the datapoint is from the current file.
    Second departure conditon: Flights that are flying and the
    previous timestamp was 15 minutes ago (equivalent of first
    data point is on air)

    Args:
        df: Flights dataframe containing the position of the flights

    Returns:
        Dataframe: Departures dataframe
    """

    complete_departures_df = df.filter(
        (df.onground)
        & (~df.next_on_ground)
        & ((df.next_actual_df == 1) | (df.next_actual_df.isNull()))
    )

    missing_departures_df = df.filter(
        (~df.onground)
        & (df.is_actual_df == 1)
        & (
            df.previous_time_position.isNull()
            | (df.time_position - df.previous_time_position > 900)
        )
    )

    departures_df = complete_departures_df.union(missing_departures_df)
    return departures_df


def get_arrivals_df(df):
    """Gets the arrivals from the flights posidtion dataframe

    First arrival condition: Flights that were flying and
    next timestamp is on ground from the current file.
    Second arrival conditon: Flights that were flying and the
    next time on air doesn't exist or is more than 15 minutes post
    (flights that landed without having datapoint on ground)

    Args:
        df: Flights dataframe containing the position of the flights

    Returns:
        Dataframe: Departures dataframe
    """
    complete_arrivals_df = df.filter(
        (~df.onground)
        & (df.next_on_ground)
        & ((df.next_actual_df == 1) | (df.next_actual_df.isNull()))
    )

    previous_arrivals_df = df.filter(
        (~df.onground)
        & (df.is_actual_df == 0)
        & (
            df.next_time_position.isNull()
            | (df.next_time_position - df.time_position > 900)
        )
    )

    arrivals_df = complete_arrivals_df.union(previous_arrivals_df)
    return arrivals_df


def distance() -> str:
    """Formula to calculate the great-circle distance

    https://en.wikipedia.org/wiki/Great-circle_distance#Formulae

    Returns:
        str: distance in km
    """
    return F.acos(
        F.sin(F.radians(col("lat"))) * F.sin(F.radians(col("latitude_deg")))
        + F.cos(F.radians(col("lat")))
        * F.cos(F.radians(col("latitude_deg")))
        * F.cos(F.radians(col("lon")) - F.radians(col("longitude_deg")))
    ) * F.lit(6371.0)


def distanceDF(df, airports_df):
    """Creates a dataframe with the distance between departures/arrivals and airports

    Args:
        df: Dataframe containing the departures/arrivals
        airports_df: Dataframe containing the airports location

    Returns:
        Dataframe: A dataframe with de between departures/arrivals and airports
    """
    return (
        df.join(airports_df)
        .select(df["*"], col("id"), col("latitude_deg"), col("longitude_deg"))
        .withColumn("distance", distance())
        .filter(col("distance") < 5.0)
    )


def getClosestAirport(df):
    """Get closest Airport to each departure/arrival

    Args:
        df: Dataframe containing the departures/arrivals and distance to each airport

    Returns:
        Dataframe: Dataframe containing the departures/arrivals and their closest airport
    """
    partition_list = ["icao24", "time_position"]
    w = Window.partitionBy(*partition_list)
    return (
        df.select(col("icao24"), col("time_position"), col("id"), col("distance"))
        .withColumn("min_distance", F.min("distance").over(w))
        .filter(col("distance") == col("min_distance"))
        .select(col("icao24"), col("time_position"), col("id"))
    )


FLIGHTS_SCHEMA = StructType(
    [
        StructField("icao24", StringType(), False),
        StructField("callsign", StringType(), True),
        StructField("origin_country", StringType(), False),
        StructField("time_position", IntegerType(), True),
        StructField("last_contact", IntegerType(), False),
        StructField("lon", FloatType(), True),
        StructField("lat", FloatType(), True),
        StructField("baro_altitude", FloatType(), True),
        StructField("onground", BooleanType(), False),
        StructField("velocity", FloatType(), True),
        StructField("true_track", FloatType(), True),
        StructField("vertical_rate", FloatType(), True),
        StructField("sensors", IntegerType(), True),
        StructField("geo_altitude", FloatType(), True),
        StructField("squawk", StringType(), True),
        StructField("spi", BooleanType(), False),
        StructField("position_source", IntegerType(), False),
    ]
)
INFILENAME = sys.argv[1]
DATE = get_current_hour_date(INFILENAME)

spark = SparkSession.builder.appName("GetDeparturesAndArrivals").getOrCreate()


previous_name = get_previous_hour_filename(INFILENAME)
try:
    previous_hour_flights_df = spark.read.csv(
        previous_name, header=False, schema=FLIGHTS_SCHEMA
    )
    previous_hour_flights_df = previous_hour_flights_df.filter(
        ~previous_hour_flights_df.time_position.isNull()
    )
    previous_hour_flights_df = previous_hour_flights_df.withColumn(
        "is_actual_df", F.lit(0)
    )
except Exception:
    print(f"Previous hour file {previous_name} not found")
    sys.exit()

current_hour_flights_df = spark.read.csv(
    INFILENAME, header=False, schema=FLIGHTS_SCHEMA
)
current_hour_flights_df = current_hour_flights_df.filter(
    ~current_hour_flights_df.time_position.isNull()
)
current_hour_flights_df = current_hour_flights_df.withColumn("is_actual_df", F.lit(1))
current_hour_flights_df = current_hour_flights_df.union(previous_hour_flights_df)

print("Two hours files read")
airports_df = spark.read.csv("gs://flights-acj/airports/airports.csv", header=True)
print("Airports read")

exploded_df = explode_flights_df(current_hour_flights_df)
print("Exploded df")

departures_df = get_departures_df(exploded_df)
print("Departures_df")

arrivals_df = get_arrivals_df(exploded_df)
print("Arrivals_df")


distance_departures_df = distanceDF(departures_df, airports_df)
print("Dsitance_departures_df")

distance_arrivals_df = distanceDF(arrivals_df, airports_df)
print("Arrivals_departures_df")


closest_airports_departures_df = getClosestAirport(distance_departures_df)
print("closest_departures_df")

closest_airports_arrivals_df = getClosestAirport(distance_arrivals_df)
print("closest_arrival_df")


closest_airports_departures_df.write.mode("overwrite").parquet(
    f"gs://flights-acj/departures/departures_{DATE}.parquet"
)
closest_airports_arrivals_df.write.mode("overwrite").parquet(
    f"gs://flights-acj/arrivals/arrivals_{DATE}.parquet"
)
