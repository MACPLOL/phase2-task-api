from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, field_validator
from database import engine
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from database import get_db
from models import Task, User
from sqlalchemy.exc import IntegrityError
from typing import Literal
from security import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

app = FastAPI()
bearer_scheme = HTTPBearer()

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

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        user_id = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    return user

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

@app.post("/users", response_model=UserResponse, status_code = 201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    safe_password = hash_password(user.password)

    new_user = User(
        email = user.email,
        hashed_password = safe_password
    )
    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail= "Email already registered",
        )
    return new_user

@app.post("/login", response_model=TokenResponse)
def login_user(
    credentials: UserLogin,
    db:Session = Depends(get_db),
):
    statement = select(User).where(User.email == credentials.email)
    result = db.execute(statement)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail= "Invalid email or password",
        )

    password_is_valid = verify_password(
    credentials.password,
    user.hashed_password,
)   
    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
    )
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user