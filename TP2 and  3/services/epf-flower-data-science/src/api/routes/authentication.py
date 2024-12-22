from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
import requests
from src.services.firebase import (
    get_users,
    set_role,
    verify_firebase_token,
    FIREBASE_SIGNUP_URL,
    FIREBASE_AUTH_URL
)

from src.schemas.firebase import RegisterRequest, FirebaseUser

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()


@router.get("/active", response_model=FirebaseUser)
def protected_route(token: str = Depends(oauth2_scheme)):
    payload: FirebaseUser = verify_firebase_token(token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"email": payload.email,
                 "user_id": payload.user_id, "role": payload.role}
    )


@router.post("/register")
def register_user(request: RegisterRequest):
    payload = {
        "email": request.email,
        "password": request.password,
        "returnSecureToken": True
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        FIREBASE_SIGNUP_URL, headers=headers, json=payload)

    if response.status_code == 200:

        if request.role:
            set_role(response.json().get("localId"), role=request.role)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Registration successful", "user_id": response.json().get(
                "localId"), "email": response.json().get("email"), "role": request.role}
        )
    else:
        error_detail = response.json().get("error", {}).get("message", "Unknown error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {error_detail}")


@router.post("/token")
def login_user(request: OAuth2PasswordRequestForm = Depends()):
    """
    Connexion d'un utilisateur via Firebase et génération d'un token JWT.
    """
    payload = {
        "email": request.username,
        "password": request.password,
        "returnSecureToken": True
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(FIREBASE_AUTH_URL, headers=headers, json=payload)

    if response.status_code == 200:
        firebase_response = response.json()

        access_token = firebase_response.get("idToken")

        return {"access_token": access_token, "token_type": "bearer"}
    else:
        error_detail = response.json().get("error", {}).get(
            "message", "Invalid credentials")
        raise HTTPException(
            status_code=400, detail=f"Login failed: {error_detail}")


def verify_admin(token: str = Depends(oauth2_scheme)):
    """ Verify if the user is an admin.

    Args:
        token (str): Firebase token

    Raises:
        HTTPException: Unauthorized access

    Returns:
        FirebaseUser: User with email, user_id and role.
    """
    payload: FirebaseUser = verify_firebase_token(token)
    if payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access"
        )
    return payload


@router.get("/users",
            response_model=list[FirebaseUser],
            dependencies=[Depends(verify_admin)])
@limiter.limit("5/minute")
def get_firebase_users(request: Request):
    users: list[FirebaseUser] = get_users()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[{"email": user.email, "user_id": user.user_id,
                  "role": user.role} for user in users]
    )
