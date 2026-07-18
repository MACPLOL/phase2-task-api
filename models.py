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