from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.college import College, Cohort
from app.models.student import StudentProfile, TrainingStatus, InternshipStatus, PlacementStatus
from app.schemas.college import CohortCreate, CohortResponse, CollegeDashboardStats, StudentSummary
from app.schemas.user import UserCreate
from app.dependencies.auth import require_roles

router = APIRouter(prefix="/colleges", tags=["College Portal"])


def get_current_college(current_user: User = Depends(require_roles(UserRole.COLLEGE)), db: Session = Depends(get_db)) -> College:
    college = db.query(College).filter(College.user_id == current_user.id).first()
    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College profile not found for this user account"
        )
    return college


@router.get("/dashboard", response_model=CollegeDashboardStats)
def get_college_dashboard(
    college: College = Depends(get_current_college),
    db: Session = Depends(get_db)
):
    students = db.query(StudentProfile).filter(StudentProfile.college_id == college.id).all()
    total = len(students)

    training_counts = {
        "completed": sum(1 for s in students if s.training_status == TrainingStatus.COMPLETED),
        "in_progress": sum(1 for s in students if s.training_status == TrainingStatus.IN_PROGRESS),
        "not_started": sum(1 for s in students if s.training_status == TrainingStatus.NOT_STARTED),
    }

    internship_counts = {
        "completed": sum(1 for s in students if s.internship_status == InternshipStatus.COMPLETED),
        "active": sum(1 for s in students if s.internship_status == InternshipStatus.ACTIVE),
        "not_started": sum(1 for s in students if s.internship_status == InternshipStatus.NOT_STARTED),
    }

    placement_counts = {
        "preparing": sum(1 for s in students if s.placement_status == PlacementStatus.PREPARING),
        "matched": sum(1 for s in students if s.placement_status == PlacementStatus.MATCHED),
        "screened": sum(1 for s in students if s.placement_status == PlacementStatus.SCREENED),
        "hospital_review": sum(1 for s in students if s.placement_status == PlacementStatus.HOSPITAL_REVIEW),
        "placed": sum(1 for s in students if s.placement_status == PlacementStatus.PLACED),
    }

    return CollegeDashboardStats(
        total_students=total,
        training=training_counts,
        internship=internship_counts,
        placement=placement_counts,
    )


@router.post("/cohorts", response_model=CohortResponse, status_code=status.HTTP_201_CREATED)
def create_cohort(
    cohort_in: CohortCreate,
    college: College = Depends(get_current_college),
    db: Session = Depends(get_db)
):
    cohort = Cohort(
        college_id=college.id,
        name=cohort_in.name,
        start_date=cohort_in.start_date,
        end_date=cohort_in.end_date,
        description=cohort_in.description,
    )
    db.add(cohort)
    db.commit()
    db.refresh(cohort)
    return CohortResponse(
        id=cohort.id,
        college_id=cohort.college_id,
        name=cohort.name,
        start_date=cohort.start_date,
        end_date=cohort.end_date,
        description=cohort.description,
        created_at=cohort.created_at,
        student_count=0
    )


@router.get("/cohorts", response_model=List[CohortResponse])
def list_cohorts(
    college: College = Depends(get_current_college),
    db: Session = Depends(get_db)
):
    cohorts = db.query(Cohort).filter(Cohort.college_id == college.id).all()
    results = []
    for c in cohorts:
        cnt = db.query(func.count(StudentProfile.id)).filter(StudentProfile.cohort_id == c.id).scalar() or 0
        results.append(
            CohortResponse(
                id=c.id,
                college_id=c.college_id,
                name=c.name,
                start_date=c.start_date,
                end_date=c.end_date,
                description=c.description,
                created_at=c.created_at,
                student_count=cnt
            )
        )
    return results


@router.get("/students", response_model=List[StudentSummary])
def list_college_students(
    college: College = Depends(get_current_college),
    cohort_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(StudentProfile).filter(StudentProfile.college_id == college.id)
    if cohort_id:
        query = query.filter(StudentProfile.cohort_id == cohort_id)
    students = query.all()

    summaries = []
    for s in students:
        cohort_name = s.cohort.name if s.cohort else None
        summaries.append(
            StudentSummary(
                id=s.id,
                user_id=s.user_id,
                full_name=s.user.full_name,
                email=s.user.email,
                phone=s.phone,
                cohort_name=cohort_name,
                training_status=s.training_status,
                internship_status=s.internship_status,
                placement_status=s.placement_status,
            )
        )
    return summaries


@router.post("/students", response_model=StudentSummary, status_code=status.HTTP_201_CREATED)
def enroll_student(
    student_in: UserCreate,
    cohort_id: int | None = None,
    college: College = Depends(get_current_college),
    db: Session = Depends(get_db)
):
    """Enrolls a student through the partner college flow."""
    existing_user = db.query(User).filter(User.email == student_in.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=student_in.email,
        hashed_password=get_password_hash(student_in.password),
        full_name=student_in.full_name,
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.flush()

    student = StudentProfile(
        user_id=user.id,
        college_id=college.id,
        cohort_id=cohort_id or student_in.cohort_id,
        training_status=TrainingStatus.NOT_STARTED,
        internship_status=InternshipStatus.NOT_STARTED,
        placement_status=PlacementStatus.PREPARING,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    cohort_name = student.cohort.name if student.cohort else None
    return StudentSummary(
        id=student.id,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=student.phone,
        cohort_name=cohort_name,
        training_status=student.training_status,
        internship_status=student.internship_status,
        placement_status=student.placement_status,
    )
