﻿# Flights-gcp

This project provides a data pipeline that given "near real time" data from planes positions inferes the departures and arrivals of flights and the airports of each one.
This personal project is the result of my learning journey in the data engineering field.

## Overview

This project provides a data pipeline that includes:

1. [**Infrastructure as Code with Terraform:**](./terraform/)

   - Infrastructure provisioning and management are handled by Terraform, facilitating reproducibility and scalability. All necessary cloud resources, including storage buckets, Dataproc clusters, Cloud Composer environments and Cloud Functions are defined and deployed via Terraform scripts.

2. [**Workflow Orchestration with Google Cloud Composer (Airflow):**](./airflow/)

   - The entire data pipeline is orchestrated and scheduled using Google Cloud Composer, which is based on Apache Airflow.

3. [**Serverless functions with Cloud Functions:**](./cloud_functions/)

   - In order to enhance the modularity of this project two cloud functions have been developed to interact with external APIs and to download external data sources.

4. [**Data Transformation with Dataproc(PySpark):**](./dataproc_scripts/)

   - Google Dataproc, powered by PySpark, is employed for efficient data processing. The extracted flight data is analyzed to extract departures and arrivals.

5. [**Final Transformation with DBT:**](./dbt/flights_de_dbt/)

   - The data in BigQuery undergoes a final transformation using DBT (Data Build Tool), allowing for the creation of business logic and data models.
     (TO-DO: Move DBT from local to Kubernetes)

6. **Data Visualization using Looker Studio:**
   - The data in BigQuery is visualized in Looker Studio. (TO-DO: Build dashboards)

## Overview

To run this project you only need a GCP account, create a project called **flights-de** and create an **owner** account called **flight-tf@flights-de.iam.gserviceaccount.com**

![Diagram](/media/diagram.png)
