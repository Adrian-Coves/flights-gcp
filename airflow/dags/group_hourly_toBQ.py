import airflow
from airflow import DAG
from airflow.operators.empty import EmptyOperator

from aux_operators.group_hourly_toBQ_operators import (
    get_previous_hour,
    createGCSToBigQuery,
    flight_dataproc_submit,
    delete_files_operator,
    group_files_operator,
    check_if_previous_file_exists,
)

from datetime import timedelta

DATASET_NAME = "flights"
ARRIVALS_TABLE_NAME = "arrivals_fact"
DEPARTURES_TABLE_NAME = "departures_fact"
BUCKET_NAME = "flights-acj"


default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


dag = DAG(
    "group_hourly_toBQ",
    default_args=default_args,
    description="Get hourly flights and upload them to big query",
    # start_date=get_start_time(),
    schedule_interval="10 * * * *",
    max_active_runs=2,
    catchup=False,
    dagrun_timeout=timedelta(minutes=35),
    is_paused_upon_creation=False,
    tags=["hourly"],
)

previous_hour = get_previous_hour()
arrivals_filename = [f"arrivals/arrivals_{previous_hour}*.parquet"]
departures_filename = [f"departures/departures_{previous_hour}*.parquet"]


start = EmptyOperator(task_id="start", dag=dag)
skip_processing = EmptyOperator(task_id="skip_processing", dag=dag)
wait_for_bq_insert = EmptyOperator(task_id="wait_for_bq_insert", dag=dag)
end = EmptyOperator(task_id="end", dag=dag)

group_files = group_files_operator(bucket=BUCKET_NAME, dag=dag)

previous_file_exists = check_if_previous_file_exists(bucket=BUCKET_NAME, dag=dag)


dataproc_operator = flight_dataproc_submit(bucket=BUCKET_NAME, dag=dag)

gcs_to_bq_departures = createGCSToBigQuery(
    source_objects=departures_filename,
    bucket=BUCKET_NAME,
    dataset=DATASET_NAME,
    table=DEPARTURES_TABLE_NAME,
    dag=dag,
)

gcs_to_bq_arrivals = createGCSToBigQuery(
    source_objects=arrivals_filename,
    bucket=BUCKET_NAME,
    dataset=DATASET_NAME,
    table=ARRIVALS_TABLE_NAME,
    dag=dag,
)


delete_old_files = delete_files_operator(bucket=BUCKET_NAME, dag=dag)


start >> group_files >> previous_file_exists
previous_file_exists >> skip_processing
previous_file_exists >> dataproc_operator
skip_processing >> delete_old_files >> end
(
    dataproc_operator
    >> [gcs_to_bq_departures, gcs_to_bq_arrivals]
    >> wait_for_bq_insert
    >> delete_old_files
)
