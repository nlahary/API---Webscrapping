from fastapi.responses import JSONResponse
from src.services.data import Dataset, get_dataset_infos, open_configs_file, write_configs_file, dump_configs_file
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/dataset/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    """ Get the information of a dataset from the configuration file

    Args:
        dataset_id (str): The name of the dataset to get

    Returns:
        Dataset: The dataset information

    Raises:
        404: The dataset was not found
    """
    dataset: Dataset = get_dataset_infos(dataset_id)
    return dataset


@router.post("/dataset")
async def post_dataset(dataset: Dataset):
    """ Add a new dataset to the configuration file

    Args:
        dataset (Dataset): The dataset to add

    Returns:
        Dataset: The dataset that was added

    Raises:
        201: The dataset was successfully added
        403: The dataset already exists
        500: The configuration file was not found / Error happened while reading it
    """
    urls = open_configs_file()
    if dataset.name in urls:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Dataset already exists: {dataset.name}. Use PUT if you wish to update it.")
    write_configs_file(dataset)
    return JSONResponse(
        content=get_dataset_infos(dataset.name).dict(),
        status_code=status.HTTP_201_CREATED
    )


@router.put("/dataset", response_model=Dataset)
async def put_dataset(dataset: Dataset):
    """ Update an existing dataset in the configuration file.
        If the dataset does not exist, it will be created and a 201 status code will be returned.

    Args:
        dataset (Dataset): The dataset to update

    Returns:
        Dataset: The updated dataset information

    Raises:
        200: The dataset was successfully updated
        201: The dataset was successfully added
        500: The configuration file was not found / Error happened while reading it / Error happened while writing it
    """
    urls = open_configs_file()
    ressource_exists = dataset.name in urls

    write_configs_file(dataset)

    updated_dataset_info = get_dataset_infos(dataset.name)
    if ressource_exists:
        return JSONResponse(
            content=updated_dataset_info.dict(),
            status_code=status.HTTP_200_OK
        )
    else:
        return JSONResponse(
            content=updated_dataset_info.dict(),
            status_code=status.HTTP_201_CREATED
        )


@router.delete("/dataset/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """ Delete a dataset from the configuration file

    Args:
        dataset_id (str): The name of the dataset to delete

    Returns:
        204: The dataset was successfully deleted

    Raises:
        404: The dataset was not found
        500: The configuration file was not found / Error happened while reading it / Error happened while writing it
    """
    datasets = open_configs_file()
    if dataset_id not in datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset not found: {dataset_id}")
    del datasets[dataset_id]
    dump_configs_file(datasets)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Dataset {dataset_id} was successfully deleted"}
    )
