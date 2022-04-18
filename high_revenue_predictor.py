from mlflow.pyfunc import PythonModel
from pypmml import Model


class HighRevenuePredictor(PythonModel):
    """High revenue predictor of flavour PyFunc."""

    def load_context(self, context):
        """Load in model saved as PMML file from MLFlow model artficats."""
        self.high_revenue_predictor_model = Model.fromFile(
            context.artifacts["high_revenue_predictor"]
        )

    def predict(self, context, model_input):
        """Make inference from new data"""
        return self.high_revenue_predictor_model.predict(model_input)
