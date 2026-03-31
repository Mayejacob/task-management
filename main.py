import asyncio
from dataclasses import Field
from http.client import HTTPException
import random
from urllib import response
from urllib.request import Request
from fastapi import FastAPI, status, Query, Depends, BackgroundTasks, UploadFile, WebSocket, WebSocketDisconnect, Response
from pydantic import BaseModel, validator, ValidationError, field_validator, computed_field, model_validator
from typing import Annotated
from datetime import datetime
import uvicorn
from dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
from pathlib import Path
import shutil
import uuid
from websocket_manager import manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'

)
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
    title: str 
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
        str_strip_whitespace = True
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

@app.post("/tasks")
async def create_task(
    task: TaskCreate, 
    current_user: dict = Depends(get_current_user),
    response: Response = None
    ):
   
    new_task = {
        "id": len(tasks) + 1,
        **task.model_dump()
    }
    tasks.append(new_task)

    # broadcast to all client
    await manager.broadcast({
        "event": "task_created",
        "message": f"New task added: {task.title}",
        "task": new_task
    })

    if response:
        response.headers["X-User-Id"] = str(current_user.get("id", ""))

    # === Fix 2: Set cookie (Correct method name) ===
    if response:
        response.set_cookie(
            key="user_id",
            value=str(current_user.get("id", "")),
            httponly=True,
            max_age=3600,          # 1 hour
            samesite="lax"
        )

    return {
        "message": "task created successfully",
        "success": True,
        "status": status.HTTP_201_CREATED,
        "data": {
            "new_task": new_task,
            "user": current_user
        }
    }

UPLOAD_DIR = Path("files")
UPLOAD_DIR.mkdir(exist_ok=True)

async def process_file(file_path: str, task_id: id):
    print(f"processing started for {task_id}: {file_path}")
    # Simulate file processing
    import asyncio
    random_delay = random.randint(1, 5)

    await asyncio.sleep(random_delay)

    print(f"processing completed for {task_id}: {file_path}")
# Background Tasks & File Uploads with UploadFile + background task to "process" file.
@app.post("/task/{task_id}/upload")
async def upload_file(
    task_id: int, 
    file: UploadFile, 
    background_tasks: BackgroundTasks
    ):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return {
            "message": "Task not found",
            "success": False,
            "status": 404
        }
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    safe_filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = UPLOAD_DIR / safe_filename
    
    try: 
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

            background_tasks.add_task(process_file, str(file_location), task_id)

            return {
                "message": "file uploaded successfully",
                "success": True,
                "status": status.HTTP_201_CREATED,
                "data": {
                    "task_id": task_id,
                    "filename": file.filename,
                    "saved_as": str(file_location)
                }
            }
    except Exception as e:
        if file_location.exists():
            file_location.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/simulate_background_task")
async def simulate_background_task(
    background_tasks: BackgroundTasks,
    minutes: int = 5,
):
    delay_minutes = random.randint(1, minutes) if minutes > 1 else 1
    delay_seconds = delay_minutes * 60

    started_at = datetime.now().isoformat()
    background_tasks.add_task(long_running_task, delay_seconds)

    return {
        "message": f"Background task scheduled to run in {delay_minutes} minute(s)",
        "success": True,
        "status": 200,
        "data": {
            "estimated_delay_minutes": delay_minutes,
            "started_at": started_at
        }
    }

async def long_running_task(delay_seconds: int):
    task_id = random.randint(1000, 9999)
    print(f"Background task {task_id} started, will run for {delay_seconds}")
    await asyncio.sleep(delay_seconds)

    print(f"[{datetime.now().isoformat()}] Background task {task_id} completed after {delay_seconds // 60} minute(s)")


@app.websocket("/ws/tasks")
async def websocket_tasks_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"New client connected. Total Clients {len(manager.active_connections)}")

    try:
        while True:
            data = await websocket.receive_text()

            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected. Remaining clients {manager.active_connections}")
    
    except Exception as e:
        print(f"websocket error: {e}")
        manager.disconnect(websocket)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger(__name__)
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} for {request.url}")
    return response

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

