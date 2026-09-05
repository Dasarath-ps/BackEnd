from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # e.g., "Berlin, Germany"
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="hospital_profile")
    job_postings = relationship("JobPosting", back_populates="hospital", cascade="all, delete-orphan")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "Staff Nurse"
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. "ICU"
    experience_required: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. "2+ years"
    required_skills: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # "ICU, Emergency Care"
    required_language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "German"
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "Berlin"
    openings_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="open")  # open, closed, filled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    hospital = relationship("Hospital", back_populates="job_postings")
    applications = relationship("Application", back_populates="job_posting", cascade="all, delete-orphan")
