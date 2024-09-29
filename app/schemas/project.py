from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from schemas.base import PyObjectId


class Project(BaseModel):
    id: PyObjectId = Field(validation_alias="_id")
    user_id: str
    name: str
    description: str
    figure_count: int
    date_created: datetime
    date_modified: datetime


class ProjectIn(BaseModel):
    name: str
    description: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
