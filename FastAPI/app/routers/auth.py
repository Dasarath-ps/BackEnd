from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.college import College
from app.models.student import StudentProfile
from app.models.job_seeker import JobSeekerProfile
from app.models.hospital import Hospital
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import (
    UserResponse,
    StudentRegister,
    JobSeekerRegister,
    HospitalRegister,
    CollegeRegister,
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/student",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as a Nursing Student",
)
def register_student(user_in: StudentRegister, db: Session = Depends(get_db)):
    """Self-registration for nursing students / trainees."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered in NurseBridge."
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.STUDENT,
        is_active=True,
    )
    db.add(user)
    db.flush()

    student_profile = StudentProfile(
        user_id=user.id,
        phone=user_in.phone,
        course=user_in.course or "Nursing",
        batch=user_in.batch,
        college_id=user_in.college_id,
        cohort_id=user_in.cohort_id,
        skills=user_in.skills,
        languages=user_in.languages,
    )
    db.add(student_profile)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/register/job-seeker",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as an independent Job Seeker (Nurse)",
)
def register_job_seeker(user_in: JobSeekerRegister, db: Session = Depends(get_db)):
    """Public self-registration for nurses looking for hospital placements."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered in NurseBridge."
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.JOB_SEEKER,
        is_active=True,
    )
    db.add(user)
    db.flush()

    profile = JobSeekerProfile(
        user_id=user.id,
        title=user_in.title or "Registered Nurse",
        experience_years=user_in.experience_years or 0,
        skills=user_in.skills,
        languages=user_in.languages,
        location=user_in.location,
        cv_url=user_in.cv_url,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/register/hospital",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a Hospital / Healthcare Facility",
)
def register_hospital(user_in: HospitalRegister, db: Session = Depends(get_db)):
    """Public self-registration for hospitals recruiting nurses."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered in NurseBridge."
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.HOSPITAL,
        is_active=True,
    )
    db.add(user)
    db.flush()

    hospital = Hospital(
        user_id=user.id,
        name=user_in.hospital_name,
        location=user_in.location,
        contact_email=user_in.contact_email or user_in.email,
        contact_person=user_in.contact_person or user_in.full_name,
        phone=user_in.phone,
    )
    db.add(hospital)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/register/college",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a Partner Nursing College",
)
def register_college(user_in: CollegeRegister, db: Session = Depends(get_db)):
    """Public self-registration for partner nursing colleges."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered in NurseBridge."
        )

    # Check for duplicate college code
    code_exists = db.query(College).filter(College.code == user_in.code).first()
    if code_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"College code '{user_in.code}' is already in use."
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.COLLEGE,
        is_active=True,
    )
    db.add(user)
    db.flush()

    college = College(
        user_id=user.id,
        name=user_in.college_name,
        code=user_in.code,
        location=user_in.location,
        contact_person=user_in.contact_person or user_in.full_name,
        phone=user_in.phone,
    )
    db.add(college)
    db.commit()
    db.refresh(user)
    return user




@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")

    token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name
    )


@router.post("/login-form", response_model=Token, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 form login endpoint to support Swagger UI Authorize modal."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
