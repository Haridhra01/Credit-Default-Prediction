from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """
    Schema used when a new user registers.
    """

    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema used when returning user information.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

class LoginRequest(BaseModel):
    """
    Schema for user login.
    """

    email: EmailStr
    password: str