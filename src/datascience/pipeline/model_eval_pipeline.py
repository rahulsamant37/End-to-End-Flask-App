from src.datascience.config.configuration import ConfigurationManager
from src.datascience.components.model_eval import ModelEval
from src.datascience import logger

STAGE_NAME="Model Evaluation Stage"

class ModelEvalTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        model_eval_config = config.get_model_eval_config()
        model_eval_config = ModelEval(config=model_eval_config)
        model_eval_config.log_into_mlflow()

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelEvalTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e