from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

tasks = []


class TaskCreate(BaseModel):
    text: str


@app.get("/")
def root():
    return {"message": "Task API is running"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.post("/tasks")
def create_task(task: TaskCreate):
    new_task = {
        "id": len(tasks) + 1,
        "text": task.text,
        "completed": False,
    }

    tasks.append(new_task)

    return new_task