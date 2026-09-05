from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class CourseMode(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class CourseEnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "German Language B1", "Professional Skills"
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mode: Mapped[CourseMode] = mapped_column(SQLEnum(CourseMode), default=CourseMode.OFFLINE, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # German, English, French
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)     # A1, A2, B1, B2, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    status: Mapped[CourseEnrollmentStatus] = mapped_column(
        SQLEnum(CourseEnrollmentStatus), default=CourseEnrollmentStatus.ENROLLED, nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    course = relationship("Course", back_populates="enrollments")
    user = relationship("User")
