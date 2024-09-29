from logging import getLogger

from core.authentication.auth_token import create_access_token
from core.storage import storage
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from schemas.user import Roles, UserIn

router = APIRouter()


@router.post("/register")
async def register_user(
    request: UserIn = Body(
        None, examples=UserIn.Config.schema_extra["examples"]
    )
) -> JSONResponse:
    logger = getLogger(__name__ + ".register_user")
    try:
        logger.info("Create user record")
        id = storage.user_create_record(
            user_data=request, role=Roles.USER, verified=True
        )
        token_data = {
            "sub": request.email,
            "id": id,
            "type": "bearer",
        }
        access_token = create_access_token(token_data)
        # api_key = generate_api_key(user_id=id)

        return JSONResponse(
            {
                "id": id,
                "access_token": access_token,
                "token_type": "bearer",
                # "api_key": api_key,
            }
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        logger.error(ex)
        if storage.user_get_record({"email": request.email}):
            storage.user_delete_record({"email": request.email})
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex
