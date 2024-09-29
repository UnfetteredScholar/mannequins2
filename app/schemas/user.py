from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field
from schemas.base import PyObjectId


class Roles(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SignInType(str, Enum):
    GOOGLE_SIGN_IN = "GOOGLE_SIGN_IN"
    NORMAL = "NORMAL"
    FACEBOOK_SIGN_IN = "FACEBOOK_SIGN_IN"


class UserStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserIn(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        schema_extra = {
            "examples": {
                "normal": {
                    "summary": "Create Demo User",
                    "description": "A **demo user** for dev purposes.",
                    "value": {
                        "username": "Demo",
                        "email": "demo@example.com",
                        "password": "demopassword",
                    },
                }
            }
        }


class User(BaseModel):
    id: PyObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    username: str
    email: str
    password: str
    role: Roles
    status: UserStatus = UserStatus.ENABLED
    sign_in_type: SignInType = "NORMAL"
    verified: bool
    figure_count: int
    date_created: datetime
    date_modified: datetime


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: Roles
    status: Optional[UserStatus] = UserStatus.ENABLED
    sign_in_type: Optional[SignInType] = "NORMAL"
    verified: bool
    figure_count: int
    date_created: datetime
    date_modified: datetime
