import airflow
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyTableOperator,
    BigQueryCreateEmptyDatasetOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)

from schemas.schemas import flights_schema
from aux_operators.create_bigquery_dataset_operators import (
    download_airport_data,
)


default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 2,
    "location": "EU",
    "project_id": "flights-de",
    "retry_delay": timedelta(minutes=2),
}


dag = DAG(
    "Create_BigQuery_dataset",
    default_args=default_args,
    description="Create bigquery dataset, flights table and upload airport data",
    schedule_interval="@once",
    max_active_runs=1,
    catchup=False,
    dagrun_timeout=timedelta(minutes=15),
    is_paused_upon_creation=False,
    tags=["once"],
)


create_bigquery_dataset = BigQueryCreateEmptyDatasetOperator(
    task_id="create_bigquery_dataset",
    dataset_id="flights",
    if_exists="ignore",
    dag=dag,
)


download_airport_data_to_gcs = download_airport_data(dag)

create_bigquery_table = BigQueryCreateEmptyTableOperator(
    task_id="create_bigquery_table",
    dataset_id="flights",
    table_id="flights_fact",
    if_exists="ignore",
    schema_fields=flights_schema,
    dag=dag,
)


load_airport_csv = GCSToBigQueryOperator(
    task_id="load_airport_csv",
    bucket="flights-acj",
    source_objects="airports/airports.csv",
    destination_project_dataset_table="flights.airports_dim",
    dag=dag,
    source_format="CSV",
    write_disposition="WRITE_TRUNCATE",
)


start = EmptyOperator(task_id="start", dag=dag)
end = EmptyOperator(task_id="end", dag=dag)

(
    start
    >> create_bigquery_dataset
    >> download_airport_data_to_gcs
    >> create_bigquery_table
    >> load_airport_csv
    >> end
)
