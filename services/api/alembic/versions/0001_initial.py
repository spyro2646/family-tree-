"""Initial identity, community, and genealogy schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table("communities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()), sa.Column("slug", sa.String(180), nullable=False, unique=True),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="private"),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table("community_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(24), nullable=False, server_default="viewer"),
        sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("community_id", "user_id", name="uq_membership_community_user"),
    )
    op.create_table("invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_email", sa.String(320), nullable=False),
        sa.Column("invited_role", sa.String(24), nullable=False, server_default="viewer"),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True)), sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_invitations_invited_email", "invitations", ["invited_email"])
    op.create_table("persons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False), sa.Column("given_name", sa.String(100)),
        sa.Column("family_name", sa.String(100)), sa.Column("birth_date", sa.Date()),
        sa.Column("birth_date_precision", sa.String(24)), sa.Column("death_date", sa.Date()),
        sa.Column("death_date_precision", sa.String(24)), sa.Column("birth_place", sa.String(200)),
        sa.Column("gender", sa.String(48)), sa.Column("occupation", sa.String(160)), sa.Column("biography", sa.Text()),
        sa.Column("living_status", sa.String(16), nullable=False, server_default="unknown"),
        sa.Column("privacy_level", sa.String(16), nullable=False, server_default="community"),
        sa.Column("linked_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("community_id", "id", name="uq_person_community_id"),
    )
    op.create_index("ix_persons_community_name", "persons", ["community_id", "display_name"])
    op.create_table("parent_child_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(24), nullable=False),
        sa.Column("confidence_level", sa.String(24), nullable=False, server_default="asserted"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["community_id", "parent_person_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["community_id", "child_person_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("community_id", "parent_person_id", "child_person_id", "relationship_type", name="uq_parent_child_edge"),
        sa.CheckConstraint("parent_person_id <> child_person_id", name="ck_parent_child_not_self"),
    )
    op.create_index("ix_parent_child_child", "parent_child_relationships", ["community_id", "child_person_id"])
    op.create_table("partnerships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("person_a_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("person_b_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partnership_type", sa.String(32), nullable=False), sa.Column("start_date", sa.Date()), sa.Column("end_date", sa.Date()),
        sa.Column("status", sa.String(20), nullable=False, server_default="current"),
        sa.ForeignKeyConstraint(["community_id", "person_a_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["community_id", "person_b_id"], ["persons.community_id", "persons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("community_id", "person_a_id", "person_b_id", "partnership_type", name="uq_partnership_edge"),
        sa.CheckConstraint("person_a_id <> person_b_id", name="ck_partnership_not_self"),
    )


def downgrade() -> None:
    op.drop_table("partnerships")
    op.drop_index("ix_parent_child_child", table_name="parent_child_relationships")
    op.drop_table("parent_child_relationships")
    op.drop_index("ix_persons_community_name", table_name="persons")
    op.drop_table("persons")
    op.drop_index("ix_invitations_invited_email", table_name="invitations")
    op.drop_table("invitations")
    op.drop_table("community_memberships")
    op.drop_table("communities")
    op.drop_table("users")
