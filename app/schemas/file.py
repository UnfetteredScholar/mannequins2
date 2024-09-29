from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from schemas.base import PyObjectId


class FileCategory(str, Enum):
    PROJECT_FILE = "project_file"


class FileMetadata(BaseModel):
    filename: str
    user_id: str
    project_id: Optional[str] = None
    group: Optional[str] = None
    category: FileCategory
    restrict_access: bool = True


class FileUpdate(BaseModel):
    filename: Optional[str] = None
    group: Optional[str] = None
    restrict_access: Optional[bool] = None


class File(BaseModel):
    id: PyObjectId = Field(validation_alias="_id")
    gridfs_id: str
    filename: str
    user_id: str
    project_id: Optional[str] = None
    group: Optional[str] = None
    category: FileCategory
    restrict_access: bool
    download_link: Optional[str] = None
    date_created: datetime
    date_modified: datetime
