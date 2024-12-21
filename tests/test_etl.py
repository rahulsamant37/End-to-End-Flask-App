import pytest
from datetime import datetime
from airflow.models import DagBag
from unittest.mock import Mock, patch
from airflow.providers.postgres.hooks.postgres import PostgresHook

def test_dag_loaded():
    """Test that the DAG is loaded correctly"""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id='weather-api-postgres')
    assert dag is not None
    assert len(dag.tasks) == 4

@pytest.fixture
def mock_weather_response():
    return {
        'current_condition': [{
            'observation_time': '12:00 PM',
            'temp_C': '25.5',
            'humidity': '65',
            'weatherDesc': [{'value': 'Partly cloudy'}]
        }]
    }

@pytest.fixture
def mock_postgres_hook():
    return Mock(spec=PostgresHook)

def test_transform_weather_data(mock_weather_response):
    """Test the transformation of weather data"""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id='weather-api-postgres')
    
    # Get transform task
    transform_task = next(task for task in dag.tasks if task.task_id == 'transform_weather_data')
    
    # Execute transformation
    result = transform_task.python_callable(mock_weather_response)
    
    assert result['location'] == 'Chandigarh'
    assert isinstance(result['observation_time'], datetime)
    assert result['temp_c'] == 25.5
    assert result['humidity'] == 65
    assert result['weather_desc'] == 'Partly cloudy'

@patch('airflow.providers.postgres.hooks.postgres.PostgresHook')
def test_create_table(mock_hook):
    """Test create table task"""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id='weather-api-postgres')
    
    # Get create table task
    create_table_task = next(task for task in dag.tasks if task.task_id == 'create_table')
    
    # Execute task
    create_table_task.python_callable()
    
    # Verify PostgresHook was called with correct SQL
    mock_hook.return_value.run.assert_called_once()
    call_args = mock_hook.return_value.run.call_args[0][0]
    assert 'CREATE TABLE IF NOT EXISTS weather_data' in call_args

def test_dag_structure():
    """Test the structure of the DAG"""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id='weather-api-postgres')
    
    tasks = dag.tasks
    task_ids = [task.task_id for task in tasks]
    
    assert 'create_table' in task_ids
    assert 'extract_weather' in task_ids
    assert 'transform_weather_data' in task_ids
    assert 'load_weather_data' in task_ids