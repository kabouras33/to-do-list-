from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the task")
    completed: bool = Field(default=False, description="Completion status of the task")

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title must not be empty')
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the task")
    completed: Optional[bool] = Field(None, description="Completion status of the task")

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title must not be empty')
        return v

class TaskInDBBase(TaskBase):
    id: int = Field(..., description="Unique identifier for the task")
    created_at: datetime = Field(..., description="Timestamp when the task was created")
    updated_at: datetime = Field(..., description="Timestamp when the task was last updated")

    class Config:
        orm_mode = True

class Task(TaskInDBBase):
    pass

class TaskInDB(TaskInDBBase):
    pass