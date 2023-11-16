from airflow.operators.bash_operator import BashOperator


def download_airport_data(dag) -> BashOperator:
    airpots_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
    task_id = "download_airport_data_to_gcs"
    bash_command = f"""
            curl -m 70 -X POST https://europe-southwest1-flights-de.cloudfunctions.net/url_to_bucket \
            -H "Authorization: bearer $(gcloud auth print-identity-token)" \
            -H "Content-Type: application/json" \
            -d '{{
                        "url": "{airpots_url}",
                        "bucket":"flights-acj",
                        "route": "airports"
                    }}'
                        """
    return BashOperator(task_id=task_id, bash_command=bash_command, dag=dag)
