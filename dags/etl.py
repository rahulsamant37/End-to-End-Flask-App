from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from json

## Define the DAG
with DAG(
    dag_id='weather-api-postgres',
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    ## Step 1: Create the table if it doesn't exists

    ## Step 2: Exract the Weather API Data (Extract Pipeline)

    ## Step 3: Transform the data (Pick the Informantion that I need to save)

    ## Step 4: Load the data into Postgres SQL

    ## Step 5: Verify the data DBViewer

    ## Step 6: Define the task dependency