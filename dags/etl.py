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

    @task
    def create_table():
        ## initialize the Postgreshook
        postgres_hook=PostgresHook(postgres_conn_id="my_postgres_connection")

        ## SQL query to create the table
        create_table_query="""
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            location VARCHAR(100),
            observation_time TIMESTAMP,
            temp_c FLOAT,
            humidity INT,
            weather_desc VARCHAR(255)
        );
        """

        ## Execute the table creation query
        postgres_hook.run(create_table_query)

    ## Step 2: Exract the Weather API Data (Extract Pipeline)
    
    extract_weather = SimpleHttpOperator(
        task_id='extract_weather',
        http_conn_id='weather_api',
        endpoint='Chandigarh?format=j1',
        method='GET',
        response_filter=lambda response: response.json(),
        log_response=True,
        dag=dag,
    )

    ## Step 3: Transform the data (Pick the Informantion that I need to save)

    @task
    def transform_weather_data(response):
        current_condition = response['current_condition'][0]
        transformed_data = {
            'location': 'Chandigarh',
            'observation_time': current_condition['observation_time'],
            'temp_c': float(current_condition['temp_C']),
            'humidity': int(current_condition['humidity']),
            'weather_desc': current_condition['weatherDesc'][0]['value'],
        }
        return transformed_data


    ## Step 4: Load the data into Postgres SQL

    ## Step 5: Verify the data DBViewer

    ## Step 6: Define the task dependency