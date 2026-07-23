from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
    CheckConstraint(
        "length(trim(text)) > 0",
        name="ck_tasks_text_not_blank",
    ),
)

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(255))
    completed: Mapped[bool] = mapped_column(default=False)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)


class User(Base):
    __tablename__ = "users"

    #the id is an int and primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    #the email is a required unique string
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    #hashed password is a string and is required to be inputted.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)