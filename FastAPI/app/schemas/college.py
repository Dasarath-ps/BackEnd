from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from app.models.student import TrainingStatus, InternshipStatus, PlacementStatus


class CohortCreate(BaseModel):
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class CohortResponse(BaseModel):
    id: int
    college_id: int
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    student_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class StudentSummary(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    cohort_name: Optional[str] = None
    training_status: TrainingStatus
    internship_status: InternshipStatus
    placement_status: PlacementStatus

    model_config = ConfigDict(from_attributes=True)


class CollegeDashboardStats(BaseModel):
    total_students: int
    training: Dict[str, int]
    internship: Dict[str, int]
    placement: Dict[str, int]
