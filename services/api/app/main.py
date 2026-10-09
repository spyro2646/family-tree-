from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import Community, Invitation, Membership, ParentChild, Partnership, Person, User
from app.schemas import (CommunityCreate, CommunityOut, InvitationAccept, InvitationCreate, LoginInput, ParentLinkCreate, PartnershipCreate,
                         PersonCreate, PersonOut, TokenOutput, UserCreate)
from app.security import (create_access_token, current_user, hash_password, require_membership,
                          verify_password)
from app.services.relationships import directed_path_exists, relationship_path

app = FastAPI(title="FamilyRoots API", version="0.1.0", openapi_url="/api/v1/openapi.json")


@app.get("/health/live", tags=["health"])
async def live() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/auth/register", response_model=TokenOutput, status_code=201, tags=["auth"])
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> TokenOutput:
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password), display_name=payload.display_name)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Account could not be created") from None
    await session.refresh(user)
    return TokenOutput(access_token=create_access_token(user.id))


@app.post("/api/v1/auth/login", response_model=TokenOutput, tags=["auth"])
async def login(payload: LoginInput, session: AsyncSession = Depends(get_session)) -> TokenOutput:
    result = await session.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()
    if user is None or user.status != "active" or not verify_password(user.password_hash, payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenOutput(access_token=create_access_token(user.id))


@app.post("/api/v1/communities", response_model=CommunityOut, status_code=201, tags=["communities"])
async def create_community(payload: CommunityCreate, user: User = Depends(current_user),
                           session: AsyncSession = Depends(get_session)) -> Community:
    if payload.visibility not in {"private", "discoverable"}:
        raise HTTPException(status_code=422, detail="Invalid visibility")
    community = Community(**payload.model_dump(), owner_user_id=user.id)
    session.add(community)
    try:
        await session.flush()
        session.add(Membership(community_id=community.id, user_id=user.id, role="owner", status="active"))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Community slug is already in use") from None
    await session.refresh(community)
    return community


@app.get("/api/v1/communities", response_model=list[CommunityOut], tags=["communities"])
async def list_communities(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)) -> list[Community]:
    result = await session.execute(select(Community).join(Membership).where(
        Membership.user_id == user.id, Membership.status == "active").order_by(Community.name))
    return list(result.scalars().all())


@app.post("/api/v1/communities/{community_id}/invitations", status_code=201, tags=["invitations"])
async def create_invitation(community_id: UUID, payload: InvitationCreate, user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await require_membership(community_id, user, session, {"owner", "admin"})
    if payload.role not in {"viewer", "editor"}:
        raise HTTPException(status_code=422, detail="Invitations can grant viewer or editor access")
    token = token_urlsafe(32)
    invitation = Invitation(community_id=community_id, invited_email=payload.email.lower(),
                            invited_role=payload.role, token_hash=sha256(token.encode()).hexdigest())
    session.add(invitation)
    await session.commit()
    # The raw token is returned once for secure manual delivery until email delivery is configured.
    return {"token": token, "expires_in_days": "7"}


@app.post("/api/v1/invitations/accept", status_code=200, tags=["invitations"])
async def accept_invitation(payload: InvitationAccept, user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    token_hash = sha256(payload.token.encode()).hexdigest()
    result = await session.execute(select(Invitation).where(Invitation.token_hash == token_hash))
    invitation = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if (invitation is None or invitation.accepted_at is not None or invitation.revoked_at is not None
            or invitation.expires_at <= now or invitation.invited_email.lower() != user.email.lower()):
        raise HTTPException(status_code=400, detail="Invitation is invalid or expired")
    membership = Membership(community_id=invitation.community_id, user_id=user.id,
                            role=invitation.invited_role, status="active")
    session.add(membership)
    invitation.accepted_at = now
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="You already belong to this community") from None
    return {"community_id": str(invitation.community_id), "status": "joined"}


@app.get("/api/v1/communities/{community_id}/persons", response_model=list[PersonOut], tags=["persons"])
async def list_persons(community_id: UUID, user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_session)) -> list[Person]:
    await require_membership(community_id, user, session)
    result = await session.execute(select(Person).where(
        Person.community_id == community_id, Person.deleted_at.is_(None),
        (Person.privacy_level != "private") | (Person.created_by == user.id)).order_by(Person.display_name))
    return list(result.scalars().all())


@app.post("/api/v1/communities/{community_id}/persons", response_model=PersonOut, status_code=201, tags=["persons"])
async def create_person(community_id: UUID, payload: PersonCreate, user: User = Depends(current_user),
                        session: AsyncSession = Depends(get_session)) -> Person:
    await require_membership(community_id, user, session, {"owner", "admin", "editor"})
    if payload.privacy_level not in {"community", "private", "public"} or payload.living_status not in {"living", "deceased", "unknown"}:
        raise HTTPException(status_code=422, detail="Invalid privacy or living status")
    person = Person(community_id=community_id, created_by=user.id, **payload.model_dump())
    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person


@app.post("/api/v1/communities/{community_id}/relationships/parents", status_code=201, tags=["relationships"])
async def add_parent_link(community_id: UUID, payload: ParentLinkCreate, user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await require_membership(community_id, user, session, {"owner", "admin", "editor"})
    if payload.parent_person_id == payload.child_person_id:
        raise HTTPException(status_code=422, detail="A person cannot be their own parent")
    people = (await session.execute(select(Person.id).where(
        Person.community_id == community_id,
        Person.id.in_([payload.parent_person_id, payload.child_person_id]),
        Person.deleted_at.is_(None)))).scalars().all()
    if len(set(people)) != 2:
        raise HTTPException(status_code=404, detail="Person not found")
    edges = (await session.execute(select(ParentChild.parent_person_id, ParentChild.child_person_id).where(
        ParentChild.community_id == community_id))).all()
    if directed_path_exists(edges, payload.child_person_id, payload.parent_person_id):
        raise HTTPException(status_code=409, detail="Relationship would create an ancestry cycle")
    session.add(ParentChild(community_id=community_id, created_by=user.id, **payload.model_dump()))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Relationship already exists") from None
    return {"status": "created"}


@app.post("/api/v1/communities/{community_id}/relationships/partnerships", status_code=201, tags=["relationships"])
async def add_partnership(community_id: UUID, payload: PartnershipCreate, user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await require_membership(community_id, user, session, {"owner", "admin", "editor"})
    if payload.person_a_id == payload.person_b_id:
        raise HTTPException(status_code=422, detail="A person cannot partner with themself")
    people = (await session.execute(select(Person.id).where(
        Person.community_id == community_id, Person.id.in_([payload.person_a_id, payload.person_b_id]),
        Person.deleted_at.is_(None)))).scalars().all()
    if len(set(people)) != 2:
        raise HTTPException(status_code=404, detail="Person not found")
    a, b = sorted([payload.person_a_id, payload.person_b_id], key=str)
    session.add(Partnership(community_id=community_id, person_a_id=a, person_b_id=b,
                            partnership_type=payload.partnership_type, start_date=payload.start_date,
                            end_date=payload.end_date))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Partnership already exists") from None
    return {"status": "created"}


@app.get("/api/v1/communities/{community_id}/relationships/path", tags=["relationships"])
async def get_relationship_path(community_id: UUID, person_a: UUID, person_b: UUID,
                               user: User = Depends(current_user), session: AsyncSession = Depends(get_session)) -> dict:
    await require_membership(community_id, user, session)
    result = await session.execute(select(Person.id).where(Person.community_id == community_id,
        Person.id.in_([person_a, person_b]), Person.deleted_at.is_(None)))
    if len(set(result.scalars().all())) != 2:
        raise HTTPException(status_code=404, detail="Person not found")
    rows = (await session.execute(select(ParentChild.parent_person_id, ParentChild.child_person_id).where(
        ParentChild.community_id == community_id))).all()
    path = relationship_path(rows, person_a, person_b)
    if path is None:
        return {"connected": False, "path": []}
    return {"connected": True, "path": [str(person_id) for person_id in path]}
