from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class TrainingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class InternshipStatus(str, Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"


class PlacementStatus(str, Enum):
    PREPARING = "preparing"
    MATCHED = "matched"
    SCREENED = "screened"
    HOSPITAL_REVIEW = "hospital_review"
    PLACED = "placed"


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    college_id: Mapped[Optional[int]] = mapped_column(ForeignKey("colleges.id"), nullable=True)
    cohort_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cohorts.id"), nullable=True)

    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    course: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "B.Sc Nursing"
    batch: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)   # e.g., "2024-2026"
    skills: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # comma-separated, e.g. "ICU, Emergency, Pediatrics"
    languages: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # comma-separated, e.g. "German (B1), English"
    
    # Progress & Pipeline statuses
    training_status: Mapped[TrainingStatus] = mapped_column(
        SQLEnum(TrainingStatus), default=TrainingStatus.NOT_STARTED, nullable=False
    )
    internship_status: Mapped[InternshipStatus] = mapped_column(
        SQLEnum(InternshipStatus), default=InternshipStatus.NOT_STARTED, nullable=False
    )
    placement_status: Mapped[PlacementStatus] = mapped_column(
        SQLEnum(PlacementStatus), default=PlacementStatus.PREPARING, nullable=False
    )

    internship_org: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assigned_hospital: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="student_profile")
    college = relationship("College", back_populates="students")
    cohort = relationship("Cohort", back_populates="students")
