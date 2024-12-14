from fastapi import status
from fastapi.exceptions import HTTPException

from src.services.firebase import FirebaseClient
from src.schemas.parameters import Parameters
from firebase_admin import firestore


class FirestoreClient(FirebaseClient):
    """Wrapper around a database"""

    def __init__(self) -> None:
        """Init the client."""
        super().__init__()
        self.db = firestore.client()

    def get(self, collection_name: str, document_id: str) -> dict:
        """Find one document by ID.
        Args:
            collection_name: The collection name
            document_id: The document id
        Return:
            Document value.
        """
        doc = self.db.collection(
            collection_name).document(document_id).get()
        if doc.exists:
            return Parameters(
                **{k: v for k, v in doc.to_dict().items() if v is not None}
            )
        raise FileExistsError(
            f"No document found at {collection_name} with the id {document_id}"
        )

    def put(self, collection_name: str, document_id: str, data: Parameters) -> status:
        """Add a document to a collection.
        Args:
            collection_name: The collection name
            document_id: The document id
            data: The data to add
        """
        existing_doc = self.db.collection(
            collection_name).document(document_id).get()
        if existing_doc.exists:
            existing_data = existing_doc.to_dict()
            if set(data.dict().keys()).issubset(existing_data.keys()):
                status_code = status.HTTP_201_CREATED
                updated_data = {**existing_data, **data.to_dict()}
            else:
                status_code = status.HTTP_200_OK
                updated_data = data.to_dict()

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No document found at {collection_name} with the id {document_id}"
            )
        self.db.collection(collection_name).document(
            document_id).set(updated_data)
        return updated_data, status_code


if __name__ == "__main__":
    firestore = FirestoreClient()
