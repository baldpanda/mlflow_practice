import pandas as pd
import requests
import pytest

MODEL_URL = "http://127.0.0.1:5001/invocations"
TRAINING_DATA_LOCATION = "./data/Orders_by_customer.csv"
RANDOM_STATE = 42


class TestHighRevenuePredictorRealTimeServing:
    """Class for acceptance tests for high revenue predictor."""

    def test_high_revenue_predictor_gives_ok_response_for_valid_data(self):
        """HighRevenuePredictor should give ok status code sample of training data."""

        # Arrange
        model_request_payload = (
            pd.read_csv(TRAINING_DATA_LOCATION)
            .sample(1, random_state=RANDOM_STATE)
            .to_json(orient="split")
        )
        headers = {"Content-type": "application/json"}
        expected_probability_of_high_revenue = 0.565

        # Act
        sut = requests.session()

        model_response = sut.post(
            data=model_request_payload, url=MODEL_URL, headers=headers
        )

        # Assert
        assert model_response.status_code == 200
        assert model_response.json()[0].get("prediction") == "True"
        assert (
            pytest.approx(model_response.json()[0].get("proba_True"), 0.001)
            == expected_probability_of_high_revenue
        )
