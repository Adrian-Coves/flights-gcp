# DBT

## Overview

This DBT project is the final step in the ETL. It relates the departues and arrivals calculated in the Dataproc cluster to get full visibilty of the flights. There are two types of models, [staging](./models/staging/) where the models represent the data extracted in Dataproc and [marts](./models/marts/) where the flights and their information are calculated.

**TODO** Right now DBT has to be run manually, in the future it will be run directly from airflow.

To run DBT you'll need the necessary libraries provided in the [requirements.txt](./requirements.txt) file.
Once DBT is install the following basics command can be run:

```shell
#To run the models
dbt run

#To run the tests
dbt test

#To generate the docs in web
dbt docs serve
```
