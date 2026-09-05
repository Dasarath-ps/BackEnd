from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class UserRole(str, Enum):
    STUDENT = "student"
    JOB_SEEKER = "job_seeker"
    HOSPITAL = "hospital"
    COLLEGE = "college"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # One-to-one relationships with profile models
    college_profile = relationship("College", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_seeker_profile = relationship("JobSeekerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    hospital_profile = relationship("Hospital", back_populates="user", uselist=False, cascade="all, delete-orphan")
