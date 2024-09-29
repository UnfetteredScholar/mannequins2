from logging import getLogger

from core.authentication.auth_middleware import authenticate_user
from core.authentication.auth_token import create_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/login")
async def login_user(
    request: OAuth2PasswordRequestForm = Depends(),
) -> JSONResponse:
    logger = getLogger(__name__ + ".login_user")
    try:
        user = authenticate_user(request.username, request.password)

        logger.info("User Authenticated")
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account not verified",
            )

        logger.info("User Verified")
        token_data = {
            "sub": user.email,
            "id": user.id,
            # "role": user.role,
            "type": "bearer",
        }
        access_token = create_access_token(token_data)
        logger.info("User Token Generated")

        return JSONResponse(
            {
                "access_token": access_token,
                "token_type": "bearer",
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            }
        )
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex
