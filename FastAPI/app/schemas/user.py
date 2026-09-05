from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class StudentRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    phone: Optional[str] = None
    course: Optional[str] = None  # e.g., "B.Sc Nursing"
    batch: Optional[str] = None   # e.g., "2024-2026"
    college_id: Optional[int] = None
    cohort_id: Optional[int] = None
    skills: Optional[str] = None
    languages: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    college_id: Optional[int] = None
    cohort_id: Optional[int] = None


class JobSeekerRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    title: Optional[str] = "Registered Nurse"
    experience_years: Optional[int] = 0
    skills: Optional[str] = None  # e.g., "ICU, Emergency Care, Critical Care"
    languages: Optional[str] = None  # e.g., "German (B2), English"
    location: Optional[str] = None  # e.g., "Munich, Germany"
    cv_url: Optional[str] = None


class HospitalRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str  # Account administrator / primary contact person
    hospital_name: str
    location: Optional[str] = None  # e.g., "Berlin, Germany"
    contact_email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None


class CollegeRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str  # College representative name
    college_name: str
    code: str = Field(..., min_length=2, max_length=50)  # e.g., "BNA-2026"
    location: Optional[str] = None  # e.g., "Berlin, Germany"
    contact_person: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
