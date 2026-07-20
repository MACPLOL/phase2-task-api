from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, field_validator
from database import engine
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from database import get_db
from models import Task
from sqlalchemy.exc import IntegrityError
from typing import Literal

app = FastAPI()

class TaskCreate(BaseModel):
    text: str
    priority: str | None = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned_text = value.strip()
        if not cleaned_text:
            raise ValueError("Task text cannot be empty")
        return cleaned_text

class TaskUpdate(BaseModel):
    text: str | None = None
    completed: bool | None = None
    priority: str | None = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned_text = value.strip()

        if not cleaned_text:
            raise ValueError("Task text cannot be empty")

        return cleaned_text

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    completed: bool
    priority: str | None = None


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
def list_tasks(limit: int = Query(default=10, ge=1, le=100),
               offset: int = Query(default=0, ge=0),
               completed: bool | None = None,
               priority: Literal["low", "medium", "high"] | None = None,
               sort_order: Literal["asc", "desc"] = "asc",
               db: Session = Depends(get_db),
):
    statement = select(Task)
    if completed is not None:
        statement = statement.where(Task.completed == completed)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    if sort_order == "desc":
        order_expression = Task.id.desc()
    else:
        order_expression = Task.id.asc()

    statement = (statement
                .order_by(order_expression)
                .offset(offset)
                .limit(limit))
    result = db.execute(statement)
    return result.scalars().all()


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        text=task.text,
        completed=False,
        priority=task.priority,
    )
    
    db.add(db_task)

    try:
        db.commit()
        db.refresh(db_task)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Task could not be saved because it violates a database rule",
        )

    return db_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
):
    
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    changes = task_update.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(task, field, value)
    try:
        db.commit()
        db.refresh(task)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Task could not be updated because it violates a database rule",
        )

    return task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    ):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
   
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}