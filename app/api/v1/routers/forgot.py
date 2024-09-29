from datetime import timedelta
from typing import Dict

from core.authentication.auth_token import (
    create_access_token,
    verify_access_token,
)
from core.authentication.hashing import hash_bcrypt
from core.mail.mail_service import send_reset_email
from core.storage import storage
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from schemas.forgot import ForgotPasswordOutput, PasswordResetRequest

router = APIRouter()


@router.post("/forgot_password", response_model=ForgotPasswordOutput)
def forgot_password(email: str = Body(embed=True)) -> JSONResponse:
    """Sends a password reset to the user's email"""
    user = storage.user_verify_record({"email": email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account not found"
        )

    reset_token = create_access_token(
        {"id": user.id, "sub": user.email, "type": "password_reset"},
        timedelta(hours=1),
    )

    send_reset_email(user.email, reset_token)

    response_message = {
        "message": "Password reset token has been sent to your email.",
        "token_expire": "1 Hour",
        "email": user.email,
    }

    return JSONResponse(response_message, status_code=200)


@router.post("/reset_password", response_model=Dict[str, str])
def reset_password(request: PasswordResetRequest) -> JSONResponse:
    """Resets a user's password"""

    try:
        token_data = verify_access_token(request.token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reset token expired",
        )

    if token_data.type != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    if token_data.email != request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email does not match token",
        )

    if request.new_password == "" or request.new_password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password"
        )

    if not storage.user_get_record({"email": token_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account not found"
        )

    update = {
        "password": hash_bcrypt(request.new_password),
    }
    storage.user_update_record(
        filter={"email": token_data.email}, update=update
    )

    return JSONResponse({"message": "Password reset successfully"})
