import os
import urllib.request
from google.cloud import storage
import flask


def url_to_bucket(request: flask.Request) -> flask.Response:
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    status, response = download_and_upload(request_json)
    return flask.Response(response, status=status, mimetype="text/plain")


def download_and_upload(request_json):
    url = request_json["url"]
    bucket = request_json["bucket"]
    route = request_json["route"]
    extension = url.split(".")[-1]
    client = storage.Client()
    filename = url.split("/")[-1]
    if extension == "csv":
        temp_file = "/tmp/csvfile.csv"  # Use a temporary file
        urllib.request.urlretrieve(url, temp_file)

        # Upload the CSV file to GCS
        bucket = client.bucket(bucket)
        blob = bucket.blob(os.path.join(route, filename))
        blob.upload_from_filename(temp_file)

        return 200, "File csv"
    else:
        return 400, "File format not valid"
