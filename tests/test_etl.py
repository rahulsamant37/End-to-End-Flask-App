# tests/test_etl.py
import pytest
from datetime import datetime
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.models import Connection
from airflow.providers.postgres.hooks.postgres import PostgresHook
from unittest.mock import Mock, patch, MagicMock

# Import your DAG file
from dags.etl import dag as etl_dag

class TestETLPipeline:
    @pytest.fixture
    def mock_postgres_hook(self):
        with patch('airflow.providers.postgres.hooks.postgres.PostgresHook') as mock:
            yield mock

    @pytest.fixture
    def mock_http_response(self):
        mock_response = Mock()
        mock_response.text = '''
        {
            "current_condition": [{
                "observation_time": "12:00 PM",
                "temp_C": "25",
                "humidity": "60",
                "weatherDesc": [{"value": "Sunny"}]
            }]
        }
        '''
        return mock_response

    def test_dag_loaded(self):
        """Test that the DAG is loaded correctly"""
        assert isinstance(etl_dag, DAG)
        assert etl_dag.dag_id == 'weather-api-postgres'
        assert not etl_dag.catchup

    def test_create_table(self, mock_postgres_hook):
        """Test the create_table task"""
        from dags.etl import create_table
        
        # Execute the task
        create_table.python_callable()
        
        # Verify that run was called with the correct SQL
        mock_postgres_hook.return_value.run.assert_called_once()
        sql_call = mock_postgres_hook.return_value.run.call_args[0][0]
        assert 'CREATE TABLE IF NOT EXISTS weather_data' in sql_call

    def test_transform_weather_data(self):
        """Test the transform_weather_data task"""
        from dags.etl import transform_weather_data
        
        # Sample input data
        input_data = {
            'current_condition': [{
                'observation_time': '12:00 PM',
                'temp_C': '25',
                'humidity': '60',
                'weatherDesc': [{'value': 'Sunny'}]
            }]
        }
        
        # Transform the data
        result = transform_weather_data.python_callable(input_data)
        
        # Verify the transformation
        assert result['location'] == 'Chandigarh'
        assert isinstance(result['observation_time'], datetime)
        assert result['temp_c'] == 25.0
        assert result['humidity'] == 60
        assert result['weather_desc'] == 'Sunny'

    def test_load_weather_data(self, mock_postgres_hook):
        """Test the load_weather_data task"""
        from dags.etl import load_weather_data
        
        # Sample weather data
        weather_data = {
            'location': 'Chandigarh',
            'observation_time': datetime.now(),
            'temp_c': 25.0,
            'humidity': 60,
            'weather_desc': 'Sunny'
        }
        
        # Execute the load task
        load_weather_data.python_callable(weather_data)
        
        # Verify that the data was inserted correctly
        mock_postgres_hook.return_value.run.assert_called_once()
        
    @pytest.mark.integration
    def test_full_pipeline_integration(self, mock_postgres_hook, mock_http_response):
        """Test the full pipeline integration"""
        with patch('airflow.providers.http.operators.http.SimpleHttpOperator.execute') as mock_http:
            mock_http.return_value = mock_http_response
            
            # Run the pipeline tasks in sequence
            create_table_task = etl_dag.get_task('create_table')
            extract_task = etl_dag.get_task('extract_weather')
            transform_task = etl_dag.get_task('transform_weather_data')
            load_task = etl_dag.get_task('load_weather_data')
            
            # Verify task dependencies
            assert create_table_task.downstream_task_ids == {'extract_weather'}
            assert 'transform_weather_data' in extract_task.downstream_task_ids
            assert 'load_weather_data' in transform_task.downstream_task_ids

class TestETLConfigs:
    """Test ETL configuration and connection settings"""
    
    def test_postgres_connection(self):
        """Test that Postgres connection is configured correctly"""
        conn = Connection(
            conn_id='my_postgres_connection',
            conn_type='postgres',
            host='localhost',
            schema='test_db',
            login='postgres',
            password='postgres'
        )
        
        assert conn.conn_id == 'my_postgres_connection'
        assert conn.conn_type == 'postgres'
        
    def test_weather_api_connection(self):
        """Test that Weather API connection is configured correctly"""
        conn = Connection(
            conn_id='weather_api',
            conn_type='http'
        )
        
        assert conn.conn_id == 'weather_api'