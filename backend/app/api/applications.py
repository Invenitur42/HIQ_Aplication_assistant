from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.job import Application, Profile
from app.services import ai as ai_service

router = APIRouter(tags=["applications"])

VALID_STATUSES = {"wishlist", "applied", "interview", "offer", "rejected"}


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    status: str = "wishlist"
    job_url: str | None = None
    location: str | None = None
    notes: str | None = None
    job_description: str | None = None
    applied_on: date | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    status: str | None = None
    job_url: str | None = None
    location: str | None = None
    notes: str | None = None
    job_description: str | None = None
    applied_on: date | None = None


class ApplicationOut(BaseModel):
    id: int
    company: str
    role: str
    status: str
    job_url: str | None
    location: str | None
    notes: str | None
    job_description: str | None
    applied_on: date | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileIn(BaseModel):
    headline: str | None = None
    summary: str | None = None
    experience: str | None = None
    skills: str | None = None
    education: str | None = None


class ProfileOut(ProfileIn):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    application_id: int | None = None
    company: str | None = None
    role: str | None = None
    job_description: str | None = None


class AIResponse(BaseModel):
    content: str


def _profile_text(profile: Profile | None) -> str:
    if not profile:
        return ""
    parts = [
        profile.headline or "",
        profile.summary or "",
        profile.experience or "",
        f"Skills: {profile.skills}" if profile.skills else "",
        f"Education: {profile.education}" if profile.education else "",
    ]
    return "\n\n".join(p for p in parts if p).strip()


@router.get("/applications/", response_model=list[ApplicationOut])
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Application)
        .filter(Application.owner_id == current_user.id)
        .order_by(Application.updated_at.desc())
        .all()
    )


@router.post("/applications/", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    body: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {VALID_STATUSES}")
    app_row = Application(owner_id=current_user.id, **body.model_dump())
    db.add(app_row)
    db.commit()
    db.refresh(app_row)
    return app_row


@router.patch("/applications/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    body: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_row = (
        db.query(Application)
        .filter(Application.id == app_id, Application.owner_id == current_user.id)
        .first()
    )
    if not app_row:
        raise HTTPException(status_code=404, detail="Application not found")
    data = body.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {VALID_STATUSES}")
    for k, v in data.items():
        setattr(app_row, k, v)
    db.commit()
    db.refresh(app_row)
    return app_row


@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_row = (
        db.query(Application)
        .filter(Application.id == app_id, Application.owner_id == current_user.id)
        .first()
    )
    if not app_row:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_row)
    db.commit()


@router.get("/profile/", response_model=ProfileOut | None)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Profile).filter(Profile.owner_id == current_user.id).first()


@router.put("/profile/", response_model=ProfileOut)
def upsert_profile(
    body: ProfileIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.owner_id == current_user.id).first()
    if not profile:
        profile = Profile(owner_id=current_user.id)
        db.add(profile)
    for k, v in body.model_dump().items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/ai/tailor-resume", response_model=AIResponse)
def tailor_resume(
    body: AIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.owner_id == current_user.id).first()
    profile_text = _profile_text(profile)
    if not profile_text:
        raise HTTPException(status_code=400, detail="Save your profile first")

    company, role, jd = body.company, body.role, body.job_description
    if body.application_id:
        app_row = (
            db.query(Application)
            .filter(Application.id == body.application_id, Application.owner_id == current_user.id)
            .first()
        )
        if not app_row:
            raise HTTPException(status_code=404, detail="Application not found")
        company = company or app_row.company
        role = role or app_row.role
        jd = jd or app_row.job_description

    if not company or not role or not jd:
        raise HTTPException(status_code=400, detail="company, role, and job_description are required")

    try:
        content = ai_service.tailor_resume(profile_text, jd, company, role)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return AIResponse(content=content)


@router.post("/ai/cover-letter", response_model=AIResponse)
def cover_letter(
    body: AIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.owner_id == current_user.id).first()
    profile_text = _profile_text(profile)
    if not profile_text:
        raise HTTPException(status_code=400, detail="Save your profile first")

    company, role, jd = body.company, body.role, body.job_description
    if body.application_id:
        app_row = (
            db.query(Application)
            .filter(Application.id == body.application_id, Application.owner_id == current_user.id)
            .first()
        )
        if not app_row:
            raise HTTPException(status_code=404, detail="Application not found")
        company = company or app_row.company
        role = role or app_row.role
        jd = jd or app_row.job_description

    if not company or not role or not jd:
        raise HTTPException(status_code=400, detail="company, role, and job_description are required")

    try:
        content = ai_service.generate_cover_letter(profile_text, jd, company, role)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return AIResponse(content=content)
