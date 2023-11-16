from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from airflow.operators.bash_operator import BashOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.operators.python import BranchPythonOperator

from google.cloud import storage
from datetime import datetime, timedelta


def get_previous_hour(hours_back=1):
    return (datetime.now() - timedelta(hours=hours_back)).strftime("%Y-%m-%d-%H")


def get_grouped_file(bucket, hours_back=1):
    previous_hour = get_previous_hour(hours_back)
    grouped_file = f"gs://{bucket}/staging/base/{previous_hour}_data.csv"
    return grouped_file


def get_file_pattern(bucket):
    previous_hour = get_previous_hour()
    file_pattern = f"gs://{bucket}/raw_data/states_{previous_hour}*.csv"
    return file_pattern


def previous_file_exists(bucket):
    name = get_grouped_file(bucket, hours_back=2)
    storage_client = storage.Client()
    print(name)
    gcp_bucket = storage_client.bucket(bucket)
    exists = storage.Blob(bucket=gcp_bucket, name=name).exists(storage_client)
    if not exists:
        return ["skip_processing"]
    else:
        return ["dataproc_get_hourly_flights"]


# def check_and_update_first_hourly_run():
#    first_hourly_run = Variable.get("FIRST_HOURLY_RUN", default_var="True")
#    if first_hourly_run == "True":
#        Variable.set("FIRST_HOURLY_RUN", "False")
#        return ["skip_processing"]
#    else:
#        return ["dataproc_get_hourly_flights"]


def createGCSToBigQuery(source_objects, bucket, dataset, table, dag):
    return GCSToBigQueryOperator(
        task_id=f"{table}_gcs_to_bigquery",
        bucket=bucket,
        source_objects=source_objects,
        destination_project_dataset_table=f"{dataset}.{table}",
        dag=dag,
        source_format="PARQUET",
        write_disposition="WRITE_APPEND",
    )


# def is_first_hour_run(dag):
#    return BranchPythonOperator(
#        task_id="is_first_hour",
#        python_callable=check_and_update_first_hourly_run,
#        dag=dag,
#    )


def check_if_previous_file_exists(bucket, dag):
    return BranchPythonOperator(
        task_id="previous_file_exists",
        python_callable=previous_file_exists,
        op_kwargs={"bucket": bucket},
        dag=dag,
    )


def flight_dataproc_submit(bucket, dag):
    grouped_file = get_grouped_file(bucket)
    pyspark_job = {
        "placement": {"cluster_name": "spark-cluster-tf"},
        "pyspark_job": {
            "main_python_file_uri": f"gs://{bucket}/dataproc_scripts/departures_arrivals_csv.py",
            "args": [grouped_file],
        },
    }
    return DataprocSubmitJobOperator(
        task_id="dataproc_get_hourly_flights",
        job=pyspark_job,
        region="europe-southwest1",
        dag=dag,
    )


def group_files_operator(bucket, dag):
    grouped_file = get_grouped_file(bucket)
    file_pattern = get_file_pattern(bucket)
    compose_bash = f"""gsutil compose {file_pattern} {grouped_file}"""
    return BashOperator(task_id="group_files", bash_command=compose_bash, dag=dag)


def delete_files_operator(bucket, dag):
    previous_hour = get_previous_hour()
    file_pattern = f"gs://{bucket}/raw_data/states_{previous_hour}*.csv"
    delete_bash = f"""gsutil rm {file_pattern}"""
    return BashOperator(
        task_id="delete_files",
        bash_command=delete_bash,
        trigger_rule="one_success",
        dag=dag,
    )
