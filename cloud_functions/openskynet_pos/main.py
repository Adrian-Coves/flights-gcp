from google.cloud import storage, secretmanager
import requests
import flask
import csv
import datetime
import os


def call_api(request: flask.Request) -> flask.Response:
    BUCKET = "flights-acj"
    ROUTE = "raw_data/"
    client = storage.Client()
    js = get_states_from_openSky()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    filename = f"states_{timestamp}.csv"
    outname = "/tmp/out.csv"
    try:
        with open(outname, "w", newline="") as f:
            writer = csv.writer(f)
            for state in js["states"]:
                out = [str(s).strip() for s in state]
                writer.writerow(out)
            blob = client.bucket(BUCKET).blob(os.path.join(ROUTE, filename))
            blob.upload_from_filename(outname)
            return flask.Response("OK", status=200, mimetype="text/plain")
    except:
        return flask.Response(
            "Couldn't get the data", status=400, mimetype="text/plain"
        )


def get_states_from_openSky():
    url = "https://opensky-network.org/api/states/all"
    token = get_token()
    auth = f"Basic {token}"
    headers = {"Authorization": auth}
    response = requests.request("GET", url, headers=headers)
    return response.json()


def get_token():
    secret_client = secretmanager.SecretManagerServiceClient()
    project_id = "flights-de"
    secret_name = "opensky_token"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = secret_client.access_secret_version(request)
    token = response.payload.data.decode("UTF-8")
    return token
