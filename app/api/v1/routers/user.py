from logging import getLogger
from typing import Dict

from core.authentication.auth_middleware import (
    authenticate_user,
    get_current_active_user,
)
from core.authentication.hashing import hash_bcrypt
from core.storage import storage
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from schemas.user import PasswordUpdate, User, UserOut, UserUpdate

router = APIRouter()


@router.get("/users/me/details", status_code=200, response_model=UserOut)
async def user_details(
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    """Gets user details"""
    # Sort out projects according to 'modified_at'
    user_out = UserOut(**current_user.model_dump())
    # current_user["projects"] = sorted(
    #     current_user["projects"],
    #     key=lambda project: project["modified_at"],
    #     reverse=True,
    # )
    return user_out


@router.patch("/users/me/details", status_code=200, response_model=UserOut)
async def update_user_details(
    input: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    """Updates a user's details"""
    logger = getLogger(__name__ + ".update_user_details")
    try:
        update = {}
        for k, v in input.model_dump().items():
            if v is not None:
                update[k] = v

        storage.user_update_record(
            filter={"_id": current_user.id}, update=update
        )

        return storage.user_verify_record({"_id": current_user.id})
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.post("/users/me/change_password", response_model=Dict[str, str])
async def change_password(
    input: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    logger = getLogger(__name__ + ".change_password")
    try:
        authenticate_user(
            email=current_user.email, password=input.old_password
        )

        if len(input.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password length."
                + " Password length must be at least 8 characters",
            )

        storage.user_update_record(
            filter={"_id": current_user.id},
            update={"password": hash_bcrypt(input.new_password)},
        )

        return JSONResponse(
            {
                "message": "Password changed successfully",
            }
        )
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.delete("/users/me")
async def delete_user(
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    # Delete user
    # settings.mongodb.delete_one({"_id": ObjectId(current_user["_id"])})
    storage.user_delete_record({"_id": current_user.id})

    return JSONResponse({"success": True})
