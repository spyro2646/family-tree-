from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=160)


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CommunityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    slug: str = Field(min_length=3, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    visibility: str = "private"


class CommunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str | None
    slug: str
    visibility: str


class PersonCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    given_name: str | None = None
    family_name: str | None = None
    birth_date: date | None = None
    birth_date_precision: str | None = None
    birth_place: str | None = None
    gender: str | None = None
    occupation: str | None = None
    biography: str | None = None
    living_status: str = "unknown"
    privacy_level: str = "community"


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    community_id: UUID
    display_name: str
    birth_date: date | None
    birth_place: str | None
    living_status: str
    privacy_level: str
    version: int


class ParentLinkCreate(BaseModel):
    parent_person_id: UUID
    child_person_id: UUID
    relationship_type: str = "biological"
    confidence_level: str = "asserted"


class PartnershipCreate(BaseModel):
    person_a_id: UUID
    person_b_id: UUID
    partnership_type: str = "partner"
    start_date: date | None = None
    end_date: date | None = None


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "viewer"


class InvitationAccept(BaseModel):
    token: str = Field(min_length=32, max_length=256)
