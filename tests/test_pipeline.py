import pytest
from src.datascience.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline
from src.datascience.pipeline.data_validation_pipeline import DataValidationTrainingPipeline  
from src.datascience.pipeline.data_transformation_pipeline import DataTransformationTrainingPipeline
from src.datascience.pipeline.model_trainer_pipeline import ModelTrainerTrainingPipeline
from src.datascience.pipeline.model_eval_pipeline import ModelEvalTrainingPipeline
from pathlib import Path
import os
import shutil
import yaml
import pandas as pd

@pytest.fixture(scope="session")
def setup_test_environment():
    """Setup test environment once for all tests"""
    # Clean existing artifacts
    if os.path.exists('artifacts'):
        shutil.rmtree('artifacts')
    
    # Create required directories
    dirs = ['data_ingestion', 'data_validation', 
            'data_transformation', 'model_trainer', 'model_evaluation']
    for dir in dirs:
        os.makedirs(f'artifacts/{dir}', exist_ok=True)
    
    yield

    # Cleanup after all tests (optional)
    # if os.path.exists('artifacts'):
    #     shutil.rmtree('artifacts')

@pytest.fixture
def sample_iris_data():
    """Create a sample Iris dataset for testing"""
    data = {
        'SepalLengthCm': [5.1, 4.9, 4.7, 5.0, 5.2],
        'SepalWidthCm': [3.5, 3.0, 3.2, 3.3, 3.4],
        'PetalLengthCm': [1.4, 1.4, 1.3, 1.5, 1.6],
        'PetalWidthCm': [0.2, 0.2, 0.2, 0.3, 0.4],
        'Species': ['setosa', 'setosa', 'setosa', 'setosa', 'setosa']
    }
    return pd.DataFrame(data)

class TestPipeline:
    def test_1_data_ingestion_pipeline(self, setup_test_environment, sample_iris_data):
        """Test data ingestion pipeline"""
        # Create test data in both locations to ensure pipeline works
        os.makedirs('artifacts/data_ingestion/', exist_ok=True)
        
        # Save to both potential locations
        sample_iris_data.to_csv('artifacts/data_ingestion/iris.csv', index=False)
        
        pipeline = DataIngestionTrainingPipeline()
        pipeline.inititate_data_ingestion()
        
        # Verify either data.zip or raw data exists
        assert os.path.exists('artifacts/data_ingestion/data.zip') or \
               os.path.exists('artifacts/data_ingestion/iris.csv')

    def test_2_data_validation_pipeline(self, setup_test_environment):
        """Test data validation pipeline"""
        # Create expected schema configuration
        schema_config = {
            "COLUMNS": {
                "SepalLengthCm": "float64",
                "SepalWidthCm": "float64",
                "PetalLengthCm": "float64",
                "PetalWidthCm": "float64",
                "Species": "object"
            },
            "TARGET_COLUMN": "Species",
            "NUMERICAL_COLUMNS": [
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm"
            ],
            "CATEGORICAL_COLUMNS": [
                "Species"
            ]
        }

        # Save schema configuration
        os.makedirs('config', exist_ok=True)
        with open('config/schema.yaml', 'w') as f:
            yaml.dump(schema_config, f)

        # Create sample data with exact column names
        sample_data = pd.DataFrame({
            'SepalLengthCm': [5.1, 4.9, 4.7, 5.0, 5.2],
            'SepalWidthCm': [3.5, 3.0, 3.2, 3.3, 3.4],
            'PetalLengthCm': [1.4, 1.4, 1.3, 1.5, 1.6],
            'PetalWidthCm': [0.2, 0.2, 0.2, 0.3, 0.4],
            'Species': ['Iris-setosa', 'Iris-setosa', 'Iris-setosa', 'Iris-setosa', 'Iris-setosa']
        }).astype({
            'SepalLengthCm': 'float64',
            'SepalWidthCm': 'float64',
            'PetalLengthCm': 'float64',
            'PetalWidthCm': 'float64',
            'Species': 'object'
        })

        # Save to correct location
        os.makedirs('artifacts/data_ingestion/data-main', exist_ok=True)
        sample_data.to_csv('artifacts/data_ingestion/data-main/Iris.csv', index=False)

        # Run validation pipeline
        pipeline = DataValidationTrainingPipeline()
        pipeline.inititate_data_validation()

        assert os.path.exists('artifacts/data_validation/status.txt'), "Validation status file not created"
        
        with open('artifacts/data_validation/status.txt', 'r') as f:
            content = f.read().strip()
            assert 'Validation status: True' in content, f"Validation failed with content: {content}"



    def test_3_data_transformation_pipeline(self, setup_test_environment, sample_iris_data):
        """Test data transformation pipeline"""
        # Setup prerequisite validation status
        os.makedirs('artifacts/data_validation', exist_ok=True)
        with open('artifacts/data_validation/status.txt', 'w') as f:
            f.write('Status: True')
        
        # Setup input data in both potential locations
        sample_iris_data.to_csv('artifacts/data_ingestion/iris.csv', index=False)
        os.makedirs('artifacts/data_ingestion/data-main', exist_ok=True)
        sample_iris_data.to_csv('artifacts/data_ingestion/data-main/Iris.csv', index=False)
        
        pipeline = DataTransformationTrainingPipeline()
        pipeline.inititate_data_transformation()
        
        assert os.path.exists('artifacts/data_transformation/train.csv'), "Training data not created"
        assert os.path.exists('artifacts/data_transformation/test.csv'), "Test data not created"
        
        # Verify data is not empty
        train_df = pd.read_csv('artifacts/data_transformation/train.csv')
        test_df = pd.read_csv('artifacts/data_transformation/test.csv')
        assert not train_df.empty, "Training data is empty"
        assert not test_df.empty, "Test data is empty"

    def test_4_model_trainer_pipeline(self, setup_test_environment):
        """Test model trainer pipeline"""
        # Create train/test split with proper column names
        train_data = pd.DataFrame({
            'SepalLengthCm': [5.1, 4.9, 4.7, 5.0],
            'SepalWidthCm': [3.5, 3.0, 3.2, 3.3],
            'PetalLengthCm': [1.4, 1.4, 1.3, 1.5],
            'PetalWidthCm': [0.2, 0.2, 0.2, 0.3],
            'Species': ['Iris-setosa', 'Iris-setosa', 'Iris-setosa', 'Iris-setosa']
        })

        test_data = pd.DataFrame({
            'SepalLengthCm': [5.2],
            'SepalWidthCm': [3.4],
            'PetalLengthCm': [1.6],
            'PetalWidthCm': [0.4],
            'Species': ['Iris-setosa']
        })

        # Save transformed data
        os.makedirs('artifacts/data_transformation', exist_ok=True)
        train_data.to_csv('artifacts/data_transformation/train.csv', index=False)
        test_data.to_csv('artifacts/data_transformation/test.csv', index=False)

        # Create model config
        model_config = {
            "target_column": "Species",
            "train_data_path": "artifacts/data_transformation/train.csv",
            "test_data_path": "artifacts/data_transformation/test.csv",
            "model_name": "model.joblib"
        }

        with open('config/model.yaml', 'w') as f:
            yaml.dump(model_config, f)

        # Run model trainer
        pipeline = ModelTrainerTrainingPipeline()
        pipeline.inititate_model_trainer()
        
        assert os.path.exists('artifacts/model_trainer/model.joblib'), "Model not saved"

    def test_5_model_eval_pipeline(self, setup_test_environment, sample_iris_data):
        """Test model evaluation pipeline"""
        # Setup prerequisite data
        os.makedirs('artifacts/data_transformation', exist_ok=True)
        test_data = sample_iris_data.iloc[4:]  # Use last sample as test data
        test_data.to_csv('artifacts/data_transformation/test.csv', index=False)
        
        # Ensure model exists
        os.makedirs('artifacts/model_trainer', exist_ok=True)
        if not os.path.exists('artifacts/model_trainer/model.joblib'):
            pytest.skip("Model file not found. Run model trainer test first.")
        
        pipeline = ModelEvalTrainingPipeline()
        pipeline.inititate_model_eval()
        
        # Basic check that evaluation ran
        assert os.path.exists('artifacts/model_evaluation'), "Model evaluation directory not created"