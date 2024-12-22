from fastapi import HTTPException, status
from firebase_admin import auth

from src.schemas.firebase import RoleEnum


def set_role(uid: int, role: str):
    if role not in RoleEnum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    custom_clains = {"role": role}
    try:
        auth.set_custom_user_claims(uid, custom_clains)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to set role: " + str(e)
        )
