from pathlib import Path
import joblib
from sklearn.metrics import accuracy_score

from src.services.train import test_train_split_iris, process_iris_df, get_iris_local

MODEL_DIR = Path(__file__).parent.parent / "models"


def predict_iris() -> list[str]:
    """ Predict the species of an iris flower

    Args:
        iris (pd.DataFrame): The iris flower to predict

    Returns:
        list[str]: The predicted species
    """
    X_train, X_test, y_train, y_test = test_train_split_iris(
        process_iris_df(get_iris_local()))
    model = joblib.load(MODEL_DIR / "iris_model.joblib")
    y_pred = model.predict(X_test)
    return y_pred
