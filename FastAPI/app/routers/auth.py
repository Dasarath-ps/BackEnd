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
from app.schemas.user import UserCreate, UserResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered in NurseBridge."
        )

    # Create base user
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Automatically initialize role-specific profile
    if user_in.role == UserRole.STUDENT:
        student_profile = StudentProfile(
            user_id=new_user.id,
            college_id=user_in.college_id,
            cohort_id=user_in.cohort_id
        )
        db.add(student_profile)
    elif user_in.role == UserRole.COLLEGE:
        college_profile = College(
            user_id=new_user.id,
            name=user_in.full_name,
            code=f"COL-{new_user.id:04d}"
        )
        db.add(college_profile)
    elif user_in.role == UserRole.JOB_SEEKER:
        job_seeker_profile = JobSeekerProfile(
            user_id=new_user.id,
            title="Registered Nurse"
        )
        db.add(job_seeker_profile)
    elif user_in.role == UserRole.HOSPITAL:
        hospital_profile = Hospital(
            user_id=new_user.id,
            name=user_in.full_name,
            contact_email=new_user.email
        )
        db.add(hospital_profile)

    db.commit()
    db.refresh(new_user)
    return new_user


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
