from logging import getLogger
from typing import List

from core.authentication.auth_middleware import get_current_active_user
from core.storage import storage
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from schemas.project import Project, ProjectIn, ProjectUpdate
from schemas.user import User

router = APIRouter()


@router.post("/projects")
async def create_project(
    input: ProjectIn,
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    """Creates a project"""
    # If the title exists return a message indicating so
    logger = getLogger(__name__ + "create_project")
    try:

        project_id = storage.project_create_record(
            project_data=input,
            user_id=current_user.id,
        )

        return JSONResponse(
            {
                "message": "Project created successfully",
                "project_id": project_id,
            }
        )
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.patch(
    "/projects/{project_id}",
)
async def update_project(
    project_id: str,
    input: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    """Updates the project specified by project_id"""
    logger = getLogger(__name__ + ".update_project")
    try:
        # Define the filter to find the user by their username
        if input.title is not None:
            existing_project = storage.project_get_record(
                filter={"user_id": current_user.id, "title": input.title}
            )

            # If the title exists return a message indicating so
            if existing_project and existing_project.id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project title already exists",
                )

        update = {}
        for k, v in input.model_dump().items():
            if v is not None:
                update[k] = v

        methodology: dict = update.pop("methodology", None)
        if methodology is not None:
            for k1, v1 in methodology.items():
                if v1 is None:
                    continue

                for k2, v2 in v1.items():
                    if v2 is not None:
                        update[f"methodology.{k1}.{k2}"] = v2

        logger.info(update)

        storage.project_update_record(
            filter={"_id": project_id, "user_id": current_user.id},
            update=update,
        )

        return JSONResponse(
            {"message": "Project updated successfully"}, status_code=200
        )
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(
    project_id: str,
    current_user: Project = Depends(get_current_active_user),
) -> Project:
    """Get project by its id"""
    logger = getLogger(__name__ + ".get_project_by_id")
    try:
        project = storage.project_verify_record(
            filter={"_id": project_id, "user_id": current_user.id}
        )

        return project
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.get("/projects", response_model=Page[Project])
async def get_projects(
    current_user: Project = Depends(get_current_active_user),
) -> List[Project]:
    """Get all projects created by the user"""
    logger = getLogger(__name__ + ".get_projects")
    try:
        projects_page = storage.project_get_page(
            filter={"user_id": current_user.id}
        )

        return projects_page
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex


@router.delete("/projects/{project_id}", status_code=200)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    """Deletes a project by its id"""
    logger = getLogger(__name__ + ".delete_project")
    try:

        storage.project_delete_record(
            filter={"_id": project_id, "user_id": current_user.id}
        )

        return JSONResponse({"message": "Project deleted"}, status_code=200)
    except Exception as ex:
        logger.error(ex)
        if type(ex) is not HTTPException:
            raise HTTPException(status_code=500, detail=str(ex))
        raise ex
