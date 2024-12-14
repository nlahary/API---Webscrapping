from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
from src.services.firestore import FirestoreClient
from src.services.firestore import Parameters

router = APIRouter()


@router.get("/parameters", response_model=Parameters)
async def get_firestore_parameters():
    try:
        firestore_client = FirestoreClient()
        params: Parameters = firestore_client.get(
            collection_name='parameters', document_id='parameters')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while fetching parameters from Firestore: {e}"
        )
    return JSONResponse(
        content=params.to_dict(),
        status_code=status.HTTP_200_OK
    )


@router.put("/parameters", response_model=Parameters)
async def put_firestore_parameters(model_params: Parameters):
    try:
        firestore_client = FirestoreClient()
        updated_params, status_code = firestore_client.put(
            collection_name='parameters', document_id='parameters', data=model_params)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while updating parameters: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while updating parameters: {e}"
        )
    return JSONResponse(
        content=updated_params,
        status_code=status_code)
