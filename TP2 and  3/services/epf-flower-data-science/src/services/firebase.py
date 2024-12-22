from src.schemas.firebase import FirebaseUser, RoleEnum
import os
from dotenv import load_dotenv
from fastapi import status, HTTPException
from firebase_admin import credentials, initialize_app, _apps
from pathlib import Path
from firebase_admin import auth

CREDENTIALS_PATH = Path(__file__).parents[4] / "creds/credentials.json"
ENV_PATH = Path(__file__).parents[2] / ".env"

load_dotenv(dotenv_path=ENV_PATH)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"


class FirebaseClient:
    """ Firebase client to initialize the app once.
        Then we can use the auth module only to interact with Firebase.
    """

    def __init__(self):
        if not _apps:
            cred = credentials.Certificate(CREDENTIALS_PATH)
            initialize_app(cred)


def get_users() -> list[FirebaseUser]:
    """ Get all users from Firebase.

    Returns:
        list[FirebaseUser]: List of Firebase users with email, user_id and role.
    """
    users_list = auth.list_users()
    users = []
    for user in users_list.iterate_all():
        users.append(FirebaseUser(email=user.email, user_id=user.uid,
                     role=user.custom_claims.get("role")))
    return users


def verify_firebase_token(token: str) -> FirebaseUser:
    """ Verify the Firebase token and return the user.

    Args:
        token (str): Firebase token

    Raises:
        HTTPException: Invalid token
        HTTPException: Token has expired
        HTTPException: Invalid token: missing required fields

    Returns:
        FirebaseUser: User with email, user_id and role.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")
        user_id = decoded_token.get("user_id")
        role = decoded_token.get("role")

        if not email or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required fields"
            )

        return FirebaseUser(email=email, user_id=user_id, role=role)

    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )


def set_role(uid: int, role: str) -> None:
    """ Set the role of a user in Firebase.

    Args:
        uid (int): User ID
        role (str): Role

    Raises:
        HTTPException: Role does not exist
        HTTPException: Failed to set role
    """
    if role not in RoleEnum.__members__:
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


def get_role(uid: int) -> str:
    """ Get the role of a user in Firebase.

    Args:
        uid (int): User ID

    Raises:
        HTTPException: Failed to get role

    Returns:
        str: Role
    """
    try:
        user = auth.get_user(uid)
        return user.custom_claims.get("role")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get role: " + str(e)
        )
