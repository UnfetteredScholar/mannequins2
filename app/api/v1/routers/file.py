import os
from io import BytesIO
from logging import getLogger
from tempfile import NamedTemporaryFile
from typing import Dict, Optional

from core.authentication.auth_middleware import get_current_active_user
from core.storage import storage
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from schemas.file import File, FileCategory, FileMetadata, FileUpdate
from schemas.user import User

router = APIRouter()


@router.post(path="/projects/{project_id}/files", response_model=File)
async def upload_project_file(
    file: UploadFile,
    project_id: str,
    file_group: Optional[str] = Form(default=None),
    restrict_access: bool = Form(default=True),
    current_user: User = Depends(get_current_active_user),
):
    """Uploads a file under a project"""

    logger = getLogger(__name__ + ".upload_project_file")
    try:
        storage.project_verify_record(
            {"_id": project_id, "user_id": current_user.id}
        )

        if file.content_type.split("/") != "image":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format",
            )

        data = await file.read()

        logger.info("Validating image content")
        temp_file_path = None

        with NamedTemporaryFile(
            mode="w+b", suffix=".pdf", delete=False
        ) as temp:
            temp.write(data)
            temp_file_path = temp.name

        # Save temp file

        file_metadata = FileMetadata(
            filename=file.filename,
            user_id=current_user.id,
            project_id=project_id,
            group=file_group,
            category=FileCategory.PROJECT_FILE,
            restrict_access=restrict_access,
        )

        id = storage.file_create_record(data=data, file_data=file_metadata)

        return storage.file_verify_record(
            {"_id": id, "user_id": current_user.id}
        )
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        pass


@router.patch(
    path="/projects/{project_id}/files/{file_id}",
    response_model=Dict[str, str],
)
async def update_project_file(
    project_id: str,
    file_id: str,
    new_values: FileUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Updates a project file's details"""

    logger = getLogger(__name__ + ".update_project_file")
    try:
        storage.project_verify_record(
            {"_id": project_id, "user_id": current_user.id}
        )
        storage.file_verify_record(
            {
                "_id": file_id,
                "project_id": project_id,
                "user_id": current_user.id,
            }
        )
        update = {}
        for k, v in new_values.model_dump().items():
            if v is not None:
                update[k] = v

        storage.file_update_record(
            filter={
                "_id": file_id,
                "project_id": project_id,
                "user_id": current_user.id,
            },
            update=update,
        )

        return JSONResponse(
            content={"message": "File updated successfully", "id": file_id}
        )
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.delete(
    path="/projects/{project_id}/files/{file_id}",
    response_model=Dict[str, str],
)
async def delete_project_file(
    project_id: str,
    file_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Deletes a file from a project"""

    logger = getLogger(__name__ + ".delete_project_file")
    try:
        storage.project_verify_record(
            {"_id": project_id, "user_id": current_user.id}
        )

        storage.file_delete_record(
            {
                "_id": file_id,
                "project_id": project_id,
                "user_id": current_user.id,
            }
        )

        return JSONResponse(content={"message": "File removed successfully"})
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.get(path="/files/{file_id}/download")
def download_file(
    file_id: str, current_user: User = Depends(get_current_active_user)
):
    """Downloads a file from the server"""
    logger = getLogger(__name__ + ".download_file")
    try:
        file = storage.file_get_record({"_id": file_id})
        logger.info("Checking for access")
        if file.restrict_access:
            if not (
                (file.user_id == current_user.id)
                or (
                    file.project_id is not None
                    and storage.project_get_record(
                        {
                            "_id": file.project_id,
                            "access_list": current_user.id,
                        }
                    )
                )
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found",
                )

        data = storage.file_get_data(file_id=file.id)
        file_like = BytesIO(data)

        response = StreamingResponse(
            file_like, media_type="application/octet-stream"
        )
        response.headers["Content-Disposition"] = (
            f"attachment; filename={file.filename}"
        )
        return response
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.get(path="/files/{file_id}/unrestricted/download")
def download_unrestricted_file(file_id: str):
    """Downloads a file from the server"""
    logger = getLogger(__name__ + ".download_unrestricted_file")
    try:
        file = storage.file_get_record({"_id": file_id})
        logger.info("Checking for access")
        if file.restrict_access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        data = storage.file_get_data(file_id=file.id)
        file_like = BytesIO(data)

        response = StreamingResponse(
            file_like, media_type="application/octet-stream"
        )
        response.headers["Content-Disposition"] = (
            f"attachment; filename={file.filename}"
        )
        return response
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex
