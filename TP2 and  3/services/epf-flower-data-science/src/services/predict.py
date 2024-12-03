from pathlib import Path
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score

from src.services.train import test_train_split_iris, process_iris_df, get_iris_local

MODEL_DIR = Path(__file__).parent.parent / "models"


def predict_iris() -> float:
    """ Predict the species of an iris flower

    Args:
        iris (pd.DataFrame): The iris flower to predict

    Returns:
        str: The species of the iris flower
    """
    X_train, X_test, y_train, y_test = test_train_split_iris(
        process_iris_df(get_iris_local()))
    model = joblib.load(MODEL_DIR / "iris_model.joblib")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy
