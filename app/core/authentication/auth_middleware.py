from typing import List

from core.authentication.auth_token import verify_access_token
from core.authentication.hashing import hash_verify
from core.storage import storage
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.token import TokenData
from schemas.user import User, UserStatus

credentials_exception: HTTPException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def authenticate_user(email: str, password: str) -> User:
    user = storage.user_verify_record({"email": email})

    if not hash_verify(hashed_password=user.password, plain_password=password):
        raise credentials_exception

    return user


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Gets the current user.

    Args:
        token: jwt string containing the user data

    Returns:
        Data about the active user
    """
    tokenData: TokenData = verify_access_token(token)

    if tokenData.type != "bearer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    user = storage.user_get_record({"email": tokenData.email})

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """
    Gets the current user and verifies if
    their account is active
    """

    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account not activated",
        )

    if user.status == UserStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account disabled",
        )

    return user


def get_current_admin_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Gets the current user and verifies if
    their account is an admin
    """

    if user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unautorized action"
        )

    return user


class RoleBasedAccessControl:
    """Defines role based access control"""

    def __init__(self, roles: List[str]) -> None:
        self.allowed_roles = roles

    def __call__(
        self, current_user: User = Depends(get_current_active_user)
    ) -> None:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not permitted to perform this action",
            )
