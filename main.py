from dataclasses import Field
from urllib import response
from fastapi import FastAPI, status, Query, Depends
from pydantic import BaseModel, validator, ValidationError, field_validator, computed_field, model_validator
from typing import Annotated
from datetime import datetime
import uvicorn
from dependencies import get_current_user

app = FastAPI()

@app.get("/")
def get_root():
    return {
        "message": "welcome to my FAStAPI application",
        "success": True,
        "status": 200
    }

@app.get("/health")
async def get_health():
    return {
        "message": "application is healthy",
        "success": True,
        "status": 200
    }

tasks = [
    {"id": 1, "title": "Task 1", "status": "pending", "priority": "high", "due_date": "2024-07-01"},
    {"id": 2, "title": "Task 2", "status": "completed", "priority": "medium", "due_date": "2024-07-05"},
    {"id": 3, "title": "Task 3", "status": "pending", "priority": "low", "due_date": "2024-07-10"},
    {"id": 4, "title": "Task 4", "status": "pending", "priority": "high", "due_date": "2024-07-15"},
    {"id": 5, "title": "Task 5", "status": "completed", "priority": "medium", "due_date": "2024-07-20"},
]
@app.get("/tasks")
async def get_tasks(
    status: str = None, 
    priority: str = None, 
    start_date: str = None, 
    end_date: str = None,
    page: int = 1,
    limit: int = Query(10, ge=10, le=100)
    ):

    filtered_tasks = tasks
    
    if status:
        filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
    if priority:
        filtered_tasks = [task for task in filtered_tasks if task["priority"] == priority]
    if start_date and end_date:
        filtered_tasks = [task for task in filtered_tasks if start_date <= task["due_date"] <= end_date]
    if start_date and not end_date:
        filtered_tasks = [task for task in filtered_tasks if task["due_date"] >= start_date] 
    if end_date and not start_date:
        filtered_tasks = [task for task in filtered_tasks if task["due_date"] <= end_date]
    
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_tasks = filtered_tasks[start_index:end_index]
    pagination_details = {
        "current_page": page,
        "total_pages": (len(filtered_tasks) + limit - 1) // limit,
        "total_tasks": len(filtered_tasks)
    }
    response_data = {
        "tasks": paginated_tasks,
        "pagination": pagination_details
    }

    return {
        "message": "tasks retrieved successfully",
        "success": True,
        "status": 200,
        "data": response_data
    }

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return {
            "message": "task not found",
            "success": False,
            "status": 404
        }
    
    return {
        "message": "task retrieved successfully",
        "success": True,
        "status": 200,
        "data": task
    }

class TaskCreate(BaseModel):
    title: str = Annotated[str, Field(min_length=1, max_length=100)],
    status: str
    priority: str
    due_date: str

    
    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values):
        if "title" not in values or not values["title"].strip():
            raise ValueError("title is required and cannot be empty")
        return values
    @model_validator(mode="after")
    @classmethod
    def validate_combined_fields(cls, values):
        if values.status == "completed" and values.due_date > datetime.now().strftime("%Y-%m-%d"):
            raise ValueError("completed tasks cannot have a due date in the future")
        return values
    
    @model_validator(mode="after")
    @classmethod
    def validate_is_overdue(cls, values):
        if values.is_overdue and values.status != "completed":
            raise ValueError("overdue tasks must be marked as completed")
        return values

    @computed_field
    def is_overdue(self) -> bool:
        return datetime.strptime(self.due_date, "%Y-%m-%d") < datetime.now()
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in ["pending", "ongoing", "started", "completed", "cancelled"]:
            raise ValueError("status must be one of: pending, ongoing, started, completed, cancelled")
        return value
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value not in ["low", "medium", "high"]:
            raise ValueError("priority must be one of: low, medium, high")
        return value
    
    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("due_date must be in the format YYYY-MM-DD")
        return value
    
    # ConfigDict
    class Config:
        anystr_strip_whitespace = True
        extra = "forbid"
        from_attributes = True
        str_to_lower = True


class TaskResponse(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    due_date: str

@app.post("/tasks_with_response_model", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    new_task = {
        "id": len(tasks) + 1,
        **task.model_dump()
    }
    tasks.append(new_task)

    return new_task

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
   
    response.header("X-user-id", str(current_user["id"]))
    
    new_task = {
        "id": len(tasks) + 1,
        **task.model_dump()
    }
    tasks.append(new_task)

    # cookies
    response.set_cookies(key="user_id", value=str(current_user["id"]), httponly=True, max_age=3600)


    return {
        "message": "task created successfully",
        "success": True,
        "status": status.HTTP_201_CREATED,
        "data": {
            "new_task": new_task,
            "user": current_user
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
