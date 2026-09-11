from datetime import datetime, timezone, date
from sqlalchemy import String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="wishlist")
    # wishlist | applied | interview | offer | rejected
    job_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="applications")


class Profile(Base):
    """Master resume / professional summary used by AI features."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience: Mapped[str | None] = mapped_column(Text, nullable=True)  # free-form bullets / text
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    education: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="profile")
