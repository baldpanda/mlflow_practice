import mlflow
import pandas as pd

FILE_PATH_TO_DATA = "./data/Orders_by_customer.csv"
LOGGED_MODEL_RUN_ID = "555015ca46b04ad981470e03eb4617eb"
LOGGED_MODEL_NAME = "model"
LOGGED_MODEL = f'runs:/{LOGGED_MODEL_RUN_ID}/{LOGGED_MODEL_NAME}'
RANDOM_STATE = 42

class TestLocalModelForRunningBatchPredictions:

    def test_running_batch_prediction_gives_expected_response(self):
        """Should be able to load model from run and use to make batch prediction."""

        # Arrange
        sut = mlflow.pyfunc.load_model(LOGGED_MODEL)

        batch_df = pd.read_csv(FILE_PATH_TO_DATA).sample(5, random_state=RANDOM_STATE)

        expected_high_revenue_predictions = ['True', 'False', 'True', 'False', 'True']

        # Act
        response = sut.predict(pd.DataFrame(batch_df))
        
        # Assert
        assert response['prediction'].to_list() == expected_high_revenue_predictions