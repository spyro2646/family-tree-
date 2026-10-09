from datetime import datetime, timezone
from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import (Date, DateTime, ForeignKey, ForeignKeyConstraint, Index,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(160))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Community(Base):
    __tablename__ = "communities"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Membership(Base):
    __tablename__ = "community_memberships"
    __table_args__ = (UniqueConstraint("community_id", "user_id"),)
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(ForeignKey("communities.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(24), default="viewer")
    status: Mapped[str] = mapped_column(String(24), default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Person(Base):
    __tablename__ = "persons"
    __table_args__ = (
        UniqueConstraint("community_id", "id"),
        Index("ix_persons_community_name", "community_id", "display_name"),
    )
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(ForeignKey("communities.id", ondelete="CASCADE"))
    display_name: Mapped[str] = mapped_column(String(200))
    given_name: Mapped[str | None] = mapped_column(String(100))
    family_name: Mapped[str | None] = mapped_column(String(100))
    birth_date: Mapped[Date | None] = mapped_column(Date)
    birth_date_precision: Mapped[str | None] = mapped_column(String(24))
    death_date: Mapped[Date | None] = mapped_column(Date)
    death_date_precision: Mapped[str | None] = mapped_column(String(24))
    birth_place: Mapped[str | None] = mapped_column(String(200))
    gender: Mapped[str | None] = mapped_column(String(48))
    occupation: Mapped[str | None] = mapped_column(String(160))
    biography: Mapped[str | None] = mapped_column(Text)
    living_status: Mapped[str] = mapped_column(String(16), default="unknown")
    privacy_level: Mapped[str] = mapped_column(String(16), default="community")
    # The authenticated account link does not establish kinship; membership is checked in services.
    linked_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1)


class ParentChild(Base):
    __tablename__ = "parent_child_relationships"
    __table_args__ = (
        UniqueConstraint("community_id", "parent_person_id", "child_person_id", "relationship_type"),
        ForeignKeyConstraint(["community_id", "parent_person_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["community_id", "child_person_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        Index("ix_parent_child_child", "community_id", "child_person_id"),
    )
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(ForeignKey("communities.id", ondelete="CASCADE"))
    parent_person_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    child_person_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    relationship_type: Mapped[str] = mapped_column(String(24))
    confidence_level: Mapped[str] = mapped_column(String(24), default="asserted")
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Partnership(Base):
    __tablename__ = "partnerships"
    __table_args__ = (
        UniqueConstraint("community_id", "person_a_id", "person_b_id", "partnership_type"),
        ForeignKeyConstraint(["community_id", "person_a_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["community_id", "person_b_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
    )
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(ForeignKey("communities.id", ondelete="CASCADE"))
    person_a_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    person_b_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    partnership_type: Mapped[str] = mapped_column(String(32))
    start_date: Mapped[Date | None] = mapped_column(Date)
    end_date: Mapped[Date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="current")


class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(ForeignKey("communities.id", ondelete="CASCADE"))
    invited_email: Mapped[str] = mapped_column(String(320), index=True)
    invited_role: Mapped[str] = mapped_column(String(24), default="viewer")
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: now_utc() + timedelta(days=7))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
