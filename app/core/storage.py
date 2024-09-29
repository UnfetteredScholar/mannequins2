from datetime import UTC, datetime
from typing import Dict, List, Optional

import gridfs
import schemas.file as s_file
import schemas.project as s_project
import schemas.user as s_user
from bson.objectid import ObjectId
from core.authentication.hashing import hash_bcrypt
from core.config import settings
from fastapi import HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.pymongo import paginate
from pymongo import ASCENDING, DESCENDING, MongoClient

# DB_NAME = "mannequins"


class MongoStorage:
    """Storage class for interfacing with mongo db"""

    def __init__(self):
        """
        Storage object with methods to Create, Read, Update,
        Delete (CRUD) objects in the mongo database.
        """
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.DB_NAME]
        self.fs = gridfs.GridFS(self.db)

        self.db["users"].create_index([("email", ASCENDING)], unique=True)
        self.db["projects"].create_index(
            [("title", ASCENDING), "user_id"], unique=True
        )

    # users
    def user_create_record(
        self,
        user_data: s_user.UserIn,
        role: s_user.Roles = "user",
        sign_in_type: s_user.SignInType = "NORMAL",
        verified: bool = False,
    ) -> str:
        """Creates a user record"""

        users_table = self.db["users"]

        if users_table.find_one({"email": user_data.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken",
            )

        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password length."
                + " Password length must be at least 8 characters",
            )

        date = datetime.now(UTC)
        user = user_data.model_dump()
        user["password"] = hash_bcrypt(user_data.password)
        user["role"] = role
        user["figure_count"] = 0
        user["sign_in_type"] = sign_in_type
        user["verified"] = verified
        user["status"] = s_user.UserStatus.ENABLED
        user["date_created"] = date
        user["date_modified"] = date

        id = str(users_table.insert_one(user).inserted_id)

        return id

    def user_get_record(self, filter: Dict) -> Optional[s_user.User]:
        """Gets a user record from the db using the supplied filter"""
        users = self.db["users"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        user = users.find_one(filter)

        if user:
            user = s_user.User(**user)

        return user

    def user_get_all_records(self, filter: Dict) -> List[s_user.User]:
        """Gets all user records from the db using the supplied filter"""
        users = self.db["users"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        users_list = users.find(filter)

        users_list = [s_user.User(**user) for user in users_list]

        return users_list

    def user_verify_record(self, filter: Dict) -> s_user.User:
        """
        Gets a user record using the filter
        and raises an error if a matching record is not found
        """

        user = self.user_get_record(filter)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    def user_update_record(self, filter: Dict, update: Dict):
        """Updates a user record"""
        self.user_verify_record(filter)

        for key in ["_id", "email"]:
            if key in update:
                raise KeyError(f"Invalid Key. KEY {key} cannot be changed")
        update["date_modified"] = datetime.now(UTC)

        return self.db["users"].update_one(filter, {"$set": update})

    def user_delete_record(self, filter: Dict):
        """Deletes a user record"""
        self.user_verify_record(filter)

        self.db["users"].delete_one(filter)

    # projects
    def project_create_record(
        self,
        project_data: s_project.ProjectIn,
        user_id: str,
    ) -> str:
        """Creates a project record"""

        projects_table = self.db["projects"]

        if projects_table.find_one(
            {"name": project_data.name, "user_id": user_id}
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project name already exists",
            )

        date = datetime.now(UTC)
        project = project_data.model_dump()
        project["user_id"] = user_id
        project["figure_count"] = 0
        project["date_created"] = date
        project["date_modified"] = date

        id = str(projects_table.insert_one(project).inserted_id)

        return id

    def project_get_record(self, filter: Dict) -> Optional[s_project.Project]:
        """Gets a project record from the db using the supplied filter"""
        projects = self.db["projects"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        project = projects.find_one(filter)

        if project:
            project = s_project.Project(**project)

        return project

    def project_get_all_records(self, filter: Dict) -> List[s_project.Project]:
        """Gets all project records from the db using the supplied filter"""
        projects = self.db["projects"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        projects_list = projects.find(filter).sort(
            {"date_modified": DESCENDING}
        )
        projects_out = []

        for project in projects_list:

            project = s_project.Project(**project)

            # project.files = self.file_get_all_records(
            #     {"project_id": project.id}
            # )
            # project.file_count = len(project.files)
            projects_out.append(project)

        return projects_out

    def project_get_page(self, filter: Dict) -> Page[s_project.Project]:
        """Gets a page of project records from
        the db using the supplied filter"""
        projects = self.db["projects"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        page: Page[s_project.Project] = paginate(
            collection=projects,
            query_filter=filter,
            sort={"date_modified": DESCENDING},
        )
        # for i, project in enumerate(page.items):
        #     project.files = self.file_get_all_records(
        #         {"project_id": project.id}
        #     )
        #     project.file_count = len(project.files)

        #     page.items[i] = project

        return page

    def project_verify_record(self, filter: Dict) -> s_project.Project:
        """
        Gets a project record using the filter
        and raises an error if a matching record is not found
        """

        project = self.project_get_record(filter)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return project

    def project_update_record(self, filter: Dict, update: Dict):
        """Updates a project record"""
        self.project_verify_record(filter)

        for key in ["_id", "user_id"]:
            if key in update:
                raise KeyError(f"Invalid Key. KEY {key} cannot be changed")
        update["date_modified"] = datetime.now(UTC)

        self.db["projects"].update_one(filter, {"$set": update})

    def project_advanced_update_record(self, filter: Dict, update: Dict):
        """Updates a project record with more complex parameters"""
        self.project_verify_record(filter)

        if "$set" in update:
            update["$set"]["date_modified"] = datetime.now(UTC)
        else:
            update["$set"] = {"date_modified": datetime.now(UTC)}

        return self.db["projects"].update_one(filter, update)

    def project_delete_record(self, filter: Dict):
        """Deletes a project record"""
        project = self.project_verify_record(filter)

        self.db["projects"].delete_one(filter)

        # for file in project.files:
        #     self.file_delete_record({"_id": file.id})

    # files
    def file_create_record(
        self,
        data: bytes,
        file_data: s_file.FileMetadata,
    ) -> str:
        """Creates a file record"""
        files_table = self.db["files"]

        gridfs_id = str(self.fs.put(data, **file_data.model_dump()))
        date = datetime.now(UTC)
        file = file_data.model_dump()
        file["gridfs_id"] = gridfs_id
        file["date_created"] = date
        file["date_modified"] = date

        id = str(files_table.insert_one(file).inserted_id)

        return id

    def file_get_record(self, filter: Dict) -> Optional[s_file.File]:
        """Gets a file record from the db using the supplied filter"""
        files = self.db["files"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        file = files.find_one(filter)

        if file:
            file = s_file.File(**file)
            if file.restrict_access:
                file.download_link = f"/api/v1/files/{file.id}/download"
            else:
                file.download_link = (
                    f"/api/v1/files/{file.id}/unrestricted/download"
                )

        return file

    def file_get_all_records(self, filter: Dict) -> List[s_file.File]:
        """Gets all file records from the db using the supplied filter"""
        files = self.db["files"]

        if "_id" in filter and type(filter["_id"]) is str:
            filter["_id"] = ObjectId(filter["_id"])

        files_list = files.find(filter)
        files_output = []

        for file in files_list:
            file = s_file.File(**file)
            if file.restrict_access:
                file.download_link = f"/api/v1/files/{file.id}/download"
            else:
                file.download_link = (
                    f"/api/v1/files/{file.id}/unrestricted/download"
                )
            files_output.append(file)

        return files_output

    def file_verify_record(self, filter: Dict) -> s_file.File:
        """
        Gets a file record using the filter
        and raises an error if a matching record is not found
        """

        file = self.file_get_record(filter)

        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        return file

    def file_get_data(self, file_id: str) -> bytes:
        """Gets the data of a file"""

        file = storage.file_verify_record({"_id": file_id})

        return self.fs.get(file_id=ObjectId(file.gridfs_id)).read()

    def file_update_record(self, filter: Dict, update: Dict):
        """Updates a file record"""
        self.file_verify_record(filter)

        for key in ["_id", "user_id", "project_id", "gridfs_id"]:
            if key in update:
                raise KeyError(f"Invalid Key. KEY {key} cannot be changed")
        update["date_modified"] = datetime.now(UTC)

        self.db["files"].update_one(filter, {"$set": update})

    def file_advanced_update_record(self, filter: Dict, update: Dict):
        """Updates a file record with more complex parameters"""
        self.file_verify_record(filter)

        if "$set" in update:
            update["$set"]["date_modified"] = datetime.now(UTC)
        else:
            update["$set"] = {"date_modified": datetime.now(UTC)}

        return self.db["files"].update_one(filter, update)

    def file_delete_record(self, filter: Dict):
        """Deletes a file record"""
        file = self.file_verify_record(filter)

        self.db["files"].delete_one(filter)
        self.fs.delete(file_id=ObjectId(file.gridfs_id))


storage = MongoStorage()
