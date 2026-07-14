from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import engine
from sqlalchemy import text

app = FastAPI()

tasks = []
next_id = 1

class TaskCreate(BaseModel):
    text: str

class TaskUpdate(BaseModel):
    text: str | None = None
    completed: bool | None = None

class TaskResponse(BaseModel):
    id: int
    text: str
    completed: bool


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return None


@app.get("/")
def root():
    return {"message": "Task API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-health")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute (text("SELECT 1")).scalar_one()

        return {"database_status": "ok", "result": result}
    
    
@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    return tasks


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    global next_id
    new_task = {
        "id": next_id,
        "text": task.text,
        "completed": False,
    }

    tasks.append(new_task)
    next_id += 1

    return new_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    changes = task_update.model_dump(exclude_unset=True)

    for field, value in changes.items():
        task[field] = value
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
   
    tasks.remove(task)
    return {"message": "Task deleted"}