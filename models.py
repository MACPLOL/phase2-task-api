from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(255))
    completed: Mapped[bool] = mapped_column(default=False)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)