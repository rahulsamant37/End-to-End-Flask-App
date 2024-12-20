# tests/test_pipeline.py
import pytest
from unittest.mock import Mock, patch
from src.datascience.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline
from src.datascience.pipeline.data_validation_pipeline import DataValidationTrainingPipeline
from src.datascience.pipeline.data_tranformation_pipeline import DataTransformationTrainingPipeline
from src.datascience.pipeline.model_trainer_pipeline import ModelTrainerTrainingPipeline
from src.datascience.pipeline.model_eval_pipeline import ModelEvalTrainingPipeline

class TestDataPipeline:
    
    @pytest.fixture
    def mock_logger(self):
        with patch('src.datascience.logger') as mock_logger:
            yield mock_logger
            
    def test_data_ingestion_pipeline(self, mock_logger):
        """Test the data ingestion pipeline stage"""
        pipeline = DataIngestionTrainingPipeline()
        
        # Mock the data ingestion process
        with patch.object(pipeline, 'initiate_data_ingestion') as mock_ingestion:
            pipeline.initiate_data_ingestion()
            
            # Assert that the method was called
            mock_ingestion.assert_called_once()
            # Verify logging
            mock_logger.info.assert_called()
            
    def test_data_validation_pipeline(self, mock_logger):
        """Test the data validation pipeline stage"""
        pipeline = DataValidationTrainingPipeline()
        
        with patch.object(pipeline, 'inititate_data_validation') as mock_validation:
            pipeline.inititate_data_validation()
            
            mock_validation.assert_called_once()
            mock_logger.info.assert_called()
            
    def test_data_transformation_pipeline(self, mock_logger):
        """Test the data transformation pipeline stage"""
        pipeline = DataTransformationTrainingPipeline()
        
        with patch.object(pipeline, 'initiate_data_ingestion') as mock_transform:
            pipeline.initiate_data_ingestion()
            
            mock_transform.assert_called_once()
            mock_logger.info.assert_called()
            
    def test_model_trainer_pipeline(self, mock_logger):
        """Test the model trainer pipeline stage"""
        pipeline = ModelTrainerTrainingPipeline()
        
        with patch.object(pipeline, 'inititate_model_trainer') as mock_trainer:
            pipeline.inititate_model_trainer()
            
            mock_trainer.assert_called_once()
            mock_logger.info.assert_called()
            
    def test_model_eval_pipeline(self, mock_logger):
        """Test the model evaluation pipeline stage"""
        pipeline = ModelEvalTrainingPipeline()
        
        with patch.object(pipeline, 'inititate_model_eval') as mock_eval:
            pipeline.inititate_model_eval()
            
            mock_eval.assert_called_once()
            mock_logger.info.assert_called()
            
    def test_pipeline_exception_handling(self, mock_logger):
        """Test exception handling in pipeline stages"""
        pipeline = DataIngestionTrainingPipeline()
        
        with patch.object(pipeline, 'initiate_data_ingestion', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as exc_info:
                pipeline.initiate_data_ingestion()
            
            assert str(exc_info.value) == "Test error"
            mock_logger.exception.assert_called_once()