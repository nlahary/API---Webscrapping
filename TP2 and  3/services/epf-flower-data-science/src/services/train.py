from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from src.services.data import test_train_split_iris, get_iris_local
from src.services.cleaning import process_iris_df
import os
from datetime import datetime
import json
import joblib
from pydantic import BaseModel
import logging

MODEL_DIR = Path(__file__).parent.parent / "models"
CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_model_config():
    """ Load the model configuration file """
    with open(CONFIG_DIR / "model_parameters.json") as file:
        return json.load(file)


def train_and_save_iris() -> str:
    """ Train the iris dataset and save the model 

    Returns:
        str: The path to the saved model+
    """
    config = load_model_config()
    X_train, _, y_train, _ = test_train_split_iris(
        process_iris_df(get_iris_local()))
    model = RandomForestClassifier(**config)
    model.fit(X_train, y_train)
    model_path = os.path.join(
        MODEL_DIR, 'iris_model.joblib')
    joblib.dump(model, model_path)
    return model_path
