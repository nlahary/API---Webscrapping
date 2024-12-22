from enum import Enum
from pydantic import BaseModel


class RoleEnum(str, Enum):
    """Enum for role options."""
    admin = "admin"
    default = "default"


class RegisterRequest(BaseModel):
    """ Firebase user credentials schema used for registration."""
    email: str
    password: str
    role: RoleEnum = None


class FirebaseUser(BaseModel):
    """ Firebase user schema."""
    email: str
    user_id: str
    role: RoleEnum
