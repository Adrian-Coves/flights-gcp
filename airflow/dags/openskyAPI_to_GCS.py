import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import timedelta


default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 0,
}


dag = DAG(
    "openskyAPI_to_GCS",
    default_args=default_args,
    description="Get current flight position from API and store it",
    schedule_interval="*/2 * * * *",  # Run every two minutes
    max_active_runs=1,
    catchup=False,
    dagrun_timeout=timedelta(minutes=1),
    is_paused_upon_creation=False,
    tags=["minute"],
)

task_id = "call_cloud_function_opensky"
bash_command = """
        curl -m 70 -X POST https://europe-southwest1-flights-de.cloudfunctions.net/openskynet_pos \
        -H "Authorization: bearer $(gcloud auth print-identity-token)" \
        -H "Content-Type: application/json" \
        """

start = EmptyOperator(task_id="start", dag=dag)
end = EmptyOperator(task_id="end", dag=dag)
call_cloud_function_opensky = BashOperator(
    task_id=task_id, bash_command=bash_command, dag=dag
)

start >> call_cloud_function_opensky >> end
