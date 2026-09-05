from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.student import StudentProfile, PlacementStatus
from app.models.course import Course, CourseEnrollment, CourseEnrollmentStatus
from app.schemas.student import (
    StudentProfileResponse,
    StudentProfileUpdate,
    PlacementPipelineResponse,
    EnrolledCourseItem,
)
from app.dependencies.auth import require_roles

router = APIRouter(prefix="/students", tags=["Student Portal"])


def get_current_student(
    current_user: User = Depends(require_roles(UserRole.STUDENT)),
    db: Session = Depends(get_db)
) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found."
        )
    return profile


@router.get("/me/profile", response_model=StudentProfileResponse)
def get_my_profile(
    student: StudentProfile = Depends(get_current_student)
):
    return StudentProfileResponse(
        id=student.id,
        user_id=student.user_id,
        full_name=student.user.full_name,
        email=student.user.email,
        phone=student.phone,
        course=student.course,
        batch=student.batch,
        college_name=student.college.name if student.college else None,
        cohort_name=student.cohort.name if student.cohort else None,
        skills=student.skills,
        languages=student.languages,
        training_status=student.training_status,
        internship_status=student.internship_status,
        placement_status=student.placement_status,
        internship_org=student.internship_org,
        assigned_hospital=student.assigned_hospital,
    )


@router.put("/me/profile", response_model=StudentProfileResponse)
def update_my_profile(
    update_data: StudentProfileUpdate,
    student: StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return get_my_profile(student)


@router.get("/me/placement-status", response_model=PlacementPipelineResponse)
def get_placement_status(student: StudentProfile = Depends(get_current_student)):
    """
    Returns the visual progression pipeline as defined in NurseBridge spec:
    Preparing -> Matched -> NurseBridge Screened -> Hospital Review -> Placed
    """
    ordered_stages = [
        ("preparing", "Preparing", "Candidate profile and prerequisites in preparation"),
        ("matched", "Matched", "Matched with healthcare provider openings"),
        ("screened", "NurseBridge Screened", "First-level clinical & language screening completed"),
        ("hospital_review", "Hospital Review", "Hospital conducting interview and review"),
        ("placed", "Placed", "Offer accepted and candidate placed"),
    ]

    stage_order = [s[0] for s in ordered_stages]
    current_index = stage_order.index(student.placement_status.value)

    steps = []
    for idx, (code, title, desc) in enumerate(ordered_stages):
        steps.append({
            "stage": code,
            "title": title,
            "description": desc,
            "is_completed": idx < current_index or (idx == current_index and student.placement_status == PlacementStatus.PLACED),
            "is_current": idx == current_index,
        })

    return PlacementPipelineResponse(
        current_status=student.placement_status,
        pipeline_steps=steps,
        assigned_hospital=student.assigned_hospital
    )


@router.get("/me/training", response_model=List[EnrolledCourseItem])
def get_my_training(
    student: StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    enrollments = db.query(CourseEnrollment).filter(CourseEnrollment.user_id == student.user_id).all()
    results = []
    for enr in enrollments:
        results.append(
            EnrolledCourseItem(
                enrollment_id=enr.id,
                course_id=enr.course_id,
                title=enr.course.title,
                mode=enr.course.mode,
                language=enr.course.language,
                level=enr.course.level,
                status=enr.status,
                enrolled_at=enr.enrolled_at,
                completed_at=enr.completed_at,
            )
        )
    return results


@router.post("/me/courses/{course_id}/enroll", response_model=EnrolledCourseItem, status_code=status.HTTP_201_CREATED)
def enroll_course(
    course_id: int,
    student: StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == student.user_id,
        CourseEnrollment.course_id == course_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled in this course")

    enrollment = CourseEnrollment(
        user_id=student.user_id,
        course_id=course_id,
        status=CourseEnrollmentStatus.ENROLLED
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return EnrolledCourseItem(
        enrollment_id=enrollment.id,
        course_id=course.id,
        title=course.title,
        mode=course.mode,
        language=course.language,
        level=course.level,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        completed_at=enrollment.completed_at,
    )
