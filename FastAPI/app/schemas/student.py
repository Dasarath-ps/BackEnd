from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.student import TrainingStatus, InternshipStatus, PlacementStatus
from app.models.course import CourseMode, CourseEnrollmentStatus


class StudentProfileUpdate(BaseModel):
    phone: Optional[str] = None
    course: Optional[str] = None
    batch: Optional[str] = None
    skills: Optional[str] = None
    languages: Optional[str] = None
    internship_org: Optional[str] = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    course: Optional[str] = None
    batch: Optional[str] = None
    college_name: Optional[str] = None
    cohort_name: Optional[str] = None
    skills: Optional[str] = None
    languages: Optional[str] = None
    training_status: TrainingStatus
    internship_status: InternshipStatus
    placement_status: PlacementStatus
    internship_org: Optional[str] = None
    assigned_hospital: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PlacementPipelineResponse(BaseModel):
    current_status: PlacementStatus
    pipeline_steps: List[dict]
    assigned_hospital: Optional[str] = None


class EnrolledCourseItem(BaseModel):
    enrollment_id: int
    course_id: int
    title: str
    mode: CourseMode
    language: Optional[str] = None
    level: Optional[str] = None
    status: CourseEnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
