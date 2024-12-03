from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
from src.services.train import train_and_save_iris, test_train_split_iris, process_iris_df, get_iris_local
from src.services.predict import predict_iris
import requests

router = APIRouter()


@router.get("/iris/load")
async def fetch_iris():
    """ Fetch the iris dataset from the configuration file

    Returns:
        Dataset: Iris dataset

    Raises:
        404: The dataset was not found
    """
    try:
        df = get_iris_local()
    except requests.exceptions.InvalidURL:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid URL provided for the dataset")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the dataset: {e}")
    return df.to_dict(orient='records')


@router.get("/iris/process")
async def process_iris():
    """ Process the iris dataset

    Returns:
        dict: The processed iris dataset

    Raises:
        500: An error occurred while processing the dataset
    """
    try:
        df = get_iris_local()
        processed_df = process_iris_df(df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the dataset: {e}")
    return processed_df.to_dict(orient='records')


@router.get("/iris/split")
async def split_iris():
    """ Split the iris dataset into training and testing sets

    Returns:
        dict: The training and testing sets

    Raises:
        500: An error occurred while splitting the dataset
    """
    try:
        X_train, X_test, y_train, y_test = test_train_split_iris(
            process_iris_df(get_iris_local()))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while splitting the dataset: {e}")
    return JSONResponse(
        content={
            "X_train": X_train.to_dict(orient='records'),
            "X_test": X_test.to_dict(orient='records'),
            "y_train": y_train.to_list(),
            "y_test": y_test.to_list()
        },
        status_code=status.HTTP_200_OK
    )


@router.get('/iris/train')
async def train_iris():

    model_path = train_and_save_iris()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "model_path": model_path
        }
    )


@router.get('/iris/predict')
async def predict():
    predicted_labels = predict_iris()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "predicted_labels": predicted_labels.tolist()
        }
    )
