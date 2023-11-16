# Cloud functions

In order to enhance the modularity of this project two cloud functions have been developed to interact with external APIs and to download external data sources.

## openskynet_pos

The [**openskynet_pos**](./openskynet_pos) is responsible for fetching real-time aircraft position data from [The OpenSky Network](https://opensky-network.org) that returns the current position of planes in the world.

This data is then stored in a CSV file named `states_{timestamp}.csv`, which is finally stored in the `flights-acj` bucket within the `raw-data/` route.

**Terms of use**

Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic, and Matthias Wilhelm.
"Bringing Up OpenSky: A Large-scale ADS-B Sensor Network for Research".
In Proceedings of the 13th IEEE/ACM International Symposium on Information Processing in Sensor Networks (IPSN), pages 83-94, April 2014.

## url_to_bucket

The **url_to_bucket** function is is designed to download a file from a specified URL and upload it to a specified route in a GCS bucket if the file format is CSV.

It expects a JSON input with the following structure:

```json
{
  "url": "string",
  "bucket": "string",
  "route": "string"
}
```
