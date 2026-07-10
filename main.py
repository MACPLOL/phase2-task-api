from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks = []
next_id = 1

class TaskCreate(BaseModel):
    text: str

class TaskUpdate(BaseModel):
    completed: bool


@app.get("/")
def root():
    return {"message": "Task API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.post("/tasks")
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

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = task_update.completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")