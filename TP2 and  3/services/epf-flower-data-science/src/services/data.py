from http.client import InvalidURL
import io
import zipfile
from fastapi import HTTPException, status
from pydantic import BaseModel, validator
import requests
from pathlib import Path
import json
import validators
import pandas as pd
from requests.exceptions import HTTPError
from sklearn.model_selection import train_test_split

JSON_CONFIG_PATH = Path(__file__).parent.parent / "config/urls_config.json"
DATA_FILE_PATH = Path(__file__).parent.parent / "data"


class Dataset(BaseModel):
    name: str
    url: str

    @validator("url")
    def url_must_be_valid(cls, url: str) -> str:
        if not validators.url(url):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid URL: {url}"
            )
        return url

    @validator("name")
    def name_must_be_valid(cls, name: str) -> str:
        if not name.isalnum():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid name: {name}"
            )
        if not isinstance(name, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Name must be a string: {name}"
            )
        return name


def open_configs_file() -> dict:
    """ Open the configuration file and return its content as a dictionary """
    try:
        with open(JSON_CONFIG_PATH) as file:
            datasets = json.load(file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration file not found: {JSON_CONFIG_PATH}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while reading the configuration file: {e}")
    else:
        return datasets


def dump_configs_file(datasets: dict) -> None:
    """ Dump the datasets dictionary to the configuration file """
    try:
        with open(JSON_CONFIG_PATH, "w") as file:
            json.dump(datasets, file, indent=4)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while writing the configuration file {e}")


def write_configs_file(dataset: Dataset) -> None:
    """ Take a dataset and write it to the configuration file """

    # We put this line out of the try block since the exceptions are already
    # handled in the open_configs_file function
    datasets = open_configs_file()
    try:
        datasets[dataset.name] = dataset.dict()
        with open(JSON_CONFIG_PATH, "w") as file:
            json.dump(datasets, file, indent=4)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while writing the configuration file {e}")


def get_dataset_infos(dataset_id: str) -> Dataset:
    """ Get the information of a dataset from the configuration file """
    try:
        datasets = open_configs_file()
        return Dataset(**datasets[dataset_id])
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Dataset not found in configuration file: {dataset_id}")


def download_dataset(dataset_url: str, dataset_name: str) -> None:
    """ Download a dataset from a URL and save it to the data folder """
    try:
        response = requests.get(dataset_url)
        output_file = DATA_FILE_PATH / f'{dataset_name}.zip'
        with open(output_file, "wb") as file:
            file.write(response.content)
    except InvalidURL:
        raise HTTPException(
            status_code=400, detail=f"Invalid URL: {dataset_url}")


def get_iris_web() -> pd.DataFrame:
    """ Download the iris dataset from the URL and return it as a Pandas DataFrame """
    iris_dataset = get_dataset_infos("iris")
    response = requests.get(iris_dataset.url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        file_names = z.namelist()
        csv_file_name = next(
            (name for name in file_names if name.endswith('.csv')), None)

        if csv_file_name is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CSV file found in the archive.")

        with z.open(csv_file_name) as csv_file:
            df = pd.read_csv(csv_file)

    return df


def get_iris_local() -> pd.DataFrame:
    """ Get the iris dataset from the data file """
    return pd.read_csv(DATA_FILE_PATH / "iris.csv")


def test_train_split_iris(iris: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """ Test the train/test split on the iris dataset and return the split as a dictionary """

    X = iris.drop(columns="species")
    y = iris["species"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test
