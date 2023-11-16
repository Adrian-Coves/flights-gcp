# Dataproc pyspark scripts

## departures_arrivals_csv

This pyspark script takes all the planes positions from the last hour and gets the departures and arrivals and the corresponding airport. Then it stores the results in GCS.

### Departures

There are two ways to identify the departures with the given data

```python
def get_departures_df(df):
    """Gets the departures from the flights position dataframe

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
```

### Arrivals

```python
def get_arrivals_df(df):
    """Gets the arrivals from the flights posidtion dataframe

    First arrival condition: Flights that were flying and
    next timestamp is on ground and the datapoint is from the current file.
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
```
