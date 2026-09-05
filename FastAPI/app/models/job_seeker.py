from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class JobSeekerProfile(Base):
    __tablename__ = "job_seeker_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), default="Registered Nurse")
    experience_years: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    skills: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # e.g., "ICU, Emergency Care"
    languages: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # e.g., "German, English"
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cv_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, verified, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="job_seeker_profile")
