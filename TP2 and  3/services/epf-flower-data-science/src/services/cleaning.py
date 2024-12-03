import pandas as pd


def process_iris_df(iris: pd.DataFrame) -> pd.DataFrame:
    COLUMNS = {
        "Id": "id",
        "SepalLengthCm": "sepal_length",
        "SepalWidthCm": "sepal_width",
        "PetalLengthCm": "petal_length",
        "PetalWidthCm": "petal_width",
        "Species": "species"
    }
    iris.rename(columns=COLUMNS, inplace=True)
    iris.species = iris.species.str.replace("Iris-", "")
    return iris
