from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    MATCHED = "matched"
    SCREENING = "screening"
    HOSPITAL_REVIEW = "hospital_review"
    OFFERED = "offered"
    PLACED = "placed"
    REJECTED = "rejected"


class InterviewOutcome(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False
    )
    match_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # e.g., 92 (%)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    job_posting = relationship("JobPosting", back_populates="applications")
    candidate = relationship("User", foreign_keys=[candidate_id])
    screening = relationship("ScreeningRecord", back_populates="application", uselist=False, cascade="all, delete-orphan")


class ScreeningRecord(Base):
    """NurseBridge Internal Screening Team records first-level interview and outcome."""
    __tablename__ = "screening_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), unique=True, nullable=False)
    screened_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    interview_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language_proficiency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    clinical_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    outcome: Mapped[InterviewOutcome] = mapped_column(
        SQLEnum(InterviewOutcome), default=InterviewOutcome.PENDING, nullable=False
    )
    screened_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="screening")
    screener = relationship("User", foreign_keys=[screened_by_id])
